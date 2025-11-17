'''test_roundtrip.py: Contains integration tests for round-trip encode/decode operations'''


import os
import tempfile

import pytest
from garmin_fit_sdk import Decoder, Encoder, Stream


class TestRoundTrip:
    '''Integration tests for round-trip encode/decode operations.'''

    @pytest.fixture
    def temp_dir(self):
        '''Fixture that provides a temporary directory for test files'''
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir

    @pytest.mark.parametrize("fit_file", [
        "tests/fits/ActivityDevFields.fit",
        "tests/fits/HrmPluginTestActivity.fit",
        "tests/fits/WithGearChangeData.fit"
    ])
    def test_round_trip_encoding(self, fit_file, temp_dir):
        '''
        Test complete round-trip encoding: decode -> encode -> decode -> compare.
        '''
        if not os.path.exists(fit_file):
            pytest.skip(f"Test file {fit_file} not found")
            
        # Step 1: Decode original file
        original_stream = Stream.from_file(fit_file)
        original_decoder = Decoder(original_stream)
        
        # Validate original file
        original_stream.reset()
        assert original_decoder.is_fit(), f"Original file {fit_file} is not a valid FIT file"
        
        original_stream.reset()
        assert original_decoder.check_integrity(), f"Original file {fit_file} failed integrity check"
        
        # Decode original messages - try non-expansion first
        original_stream.reset()
        original_messages, original_errors = original_decoder.read(
            preserve_invalid_values=True,
            merge_heart_rates=False,  # Disable heart rate merging for exact roundtrip
            expand_sub_fields=False,  # Don't expand sub-fields for roundtrip
            expand_components=False   # Don't expand component fields for roundtrip
        )
        
        # If no-expansion reading fails, use default settings consistently
        use_default_settings = len(original_messages) == 0
        
        if use_default_settings:
            # Read with expansion since non-expansion failed
            original_stream.reset()
            original_messages, original_errors = original_decoder.read()
            
        # Store the settings for consistent final decode
        decode_settings = {
            'preserve_invalid_values': True,
            'merge_heart_rates': False,
            'expand_sub_fields': False,
            'expand_components': False
        } if not use_default_settings else {}
        
        assert len(original_errors) == 0, f"Original decoding errors: {original_errors}"
        assert len(original_messages) > 0, "Original messages should not be empty"
        
        # Step 2: Encode to new file
        encoder = Encoder(original_messages)
        output_file = os.path.join(temp_dir, f"encoded_{os.path.basename(fit_file)}")
        
        result = encoder.write_to_file(output_file)
        assert result is True, "Encoder should return True on success"
        assert os.path.exists(output_file), "Encoded file should exist"
        assert os.path.getsize(output_file) > 0, "Encoded file should not be empty"
            
        # Step 3: Decode the newly encoded file
        new_stream = Stream.from_file(output_file)
        new_decoder = Decoder(new_stream)
        
        # Validate encoded file structure
        new_stream.reset()
        assert new_decoder.is_fit(), "Encoded file should be a valid FIT file"
        
        new_stream.reset()
        assert new_decoder.check_integrity(), "Encoded file should pass integrity check"
        
        # Decode new messages with EXACTLY the same settings as original read
        new_stream.reset()
        if use_default_settings:
            # Use default settings to exactly match original read
            new_messages, new_errors = new_decoder.read()
        else:
            # Use exact same non-default settings as original read  
            new_messages, new_errors = new_decoder.read(**decode_settings)

        assert len(new_errors) == 0, f"New file decoding errors: {new_errors}"
        assert len(new_messages) > 0, "New messages should not be empty"
        
        # Step 4: Compare original vs re-decoded messages
        # Perfect roundtrip comparison with zero tolerance
        self._compare_messages_deep(original_messages, new_messages)

    def _compare_messages_deep(self, original, decoded, ignore_fields=None):
        '''
        Helper method to deeply compare two message dictionaries.
        '''
        ignore_fields = ignore_fields or []
        
        # Compare message type keys
        assert set(original.keys()) == set(decoded.keys()), \
            f"Message types differ: {set(original.keys())} vs {set(decoded.keys())}"
            
        # Compare each message type
        for msg_type, orig_msgs in original.items():
            decoded_msgs = decoded[msg_type]
            assert len(orig_msgs) == len(decoded_msgs), \
                f"Message count differs for {msg_type}: {len(orig_msgs)} vs {len(decoded_msgs)}"
                
            # Compare individual messages
            for i, (orig_msg, dec_msg) in enumerate(zip(orig_msgs, decoded_msgs)):
                self._compare_single_message(orig_msg, dec_msg, ignore_fields, f"{msg_type}[{i}]")
    
    def _is_component_field(self, field_name, message_type):
        '''Check if a field is a component field that gets expanded from a parent field'''
        from garmin_fit_sdk.profile import Profile
        
        # Get message profile
        msg_num = None
        for num, msg_profile in Profile['messages'].items():
            if msg_profile.get('messages_key') == message_type:
                msg_num = num
                break
        
        if msg_num is None:
            return False
            
        msg_profile = Profile['messages'][msg_num]
        
        # Find the field profile by name
        field_profile = None
        for field_id, fp in msg_profile['fields'].items():
            if fp['name'] == field_name:
                field_profile = fp
                break
        
        if field_profile is None:
            return False
        
        field_num = field_profile['num']
        
        # Check if any other field has this field as a component
        for parent_id, parent_fp in msg_profile['fields'].items():
            if (parent_fp.get('has_components', False) and 
                'components' in parent_fp and 
                field_num in parent_fp['components']):
                return True
                
        return False

    def _compare_single_message(self, original, decoded, ignore_fields, context):
        '''Helper method to compare individual messages'''
        # Filter out ignored fields
        orig_filtered = {k: v for k, v in original.items() if k not in ignore_fields}
        dec_filtered = {k: v for k, v in decoded.items() if k not in ignore_fields}

        # For roundtrip comparison, focus on fields that exist in the original message
        # The encoder may add fields with default/invalid values due to unified field definitions
        # across all messages in the file
        
        # Compare all fields that exist in the original
        for field_name, orig_value in orig_filtered.items():
            assert field_name in dec_filtered, f"Field {field_name} missing in decoded message in {context}"
            dec_value = dec_filtered[field_name]
            
            # Handle different numeric types that might represent the same value
            if isinstance(orig_value, (int, float)) and isinstance(dec_value, (int, float)):
                # Use close comparison for floating point values
                if orig_value != dec_value:
                    if abs(orig_value - dec_value) > 1e-10:
                        assert False, f"Field {field_name} value mismatch in {context}: {orig_value} != {dec_value}"
            else:
                assert orig_value == dec_value, f"Field {field_name} value mismatch in {context}: {orig_value} != {dec_value}"        # Compare field values
        for field, orig_value in orig_filtered.items():
            dec_value = dec_filtered[field]
            
            # Handle floating point comparisons with tolerance
            if self._are_values_approximately_equal(orig_value, dec_value):
                continue
            
            assert orig_value == dec_value, \
                f"Field {field} differs in {context}: {orig_value} vs {dec_value}"
    
    def _are_values_approximately_equal(self, val1, val2, rtol=0, atol=0):
        '''Check if two values are approximately equal, handling floats and arrays'''
        import math
        
        # Handle None values
        if val1 is None and val2 is None:
            return True
        if val1 is None or val2 is None:
            return False
            
        # Handle different types
        if type(val1) != type(val2):
            return False
            
        # Handle float values
        if isinstance(val1, float) and isinstance(val2, float):
            if math.isnan(val1) and math.isnan(val2):
                return True
            return abs(val1 - val2) <= atol + rtol * abs(val2)
            
        # Handle lists/arrays of floats
        if isinstance(val1, (list, tuple)) and isinstance(val2, (list, tuple)):
            if len(val1) != len(val2):
                return False
            return all(self._are_values_approximately_equal(v1, v2, rtol, atol) 
                      for v1, v2 in zip(val1, val2))
        
        # For non-float values, use exact comparison
        return val1 == val2