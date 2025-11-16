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
        
        # Decode original messages
        original_stream.reset()
        original_messages, original_errors = original_decoder.read()
        
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
        
        # Decode new messages
        new_stream.reset()
        new_messages, new_errors = new_decoder.read()
        
        assert len(new_errors) == 0, f"New file decoding errors: {new_errors}"
        assert len(new_messages) > 0, "New messages should not be empty"
        
        # Step 4: Compare original vs re-decoded messages
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
    
    def _compare_single_message(self, original, decoded, ignore_fields, context):
        '''Helper method to compare individual messages'''
        # Filter out ignored fields
        orig_filtered = {k: v for k, v in original.items() if k not in ignore_fields}
        dec_filtered = {k: v for k, v in decoded.items() if k not in ignore_fields}
        
        # Compare field keys
        assert set(orig_filtered.keys()) == set(dec_filtered.keys()), \
            f"Field keys differ in {context}: {set(orig_filtered.keys())} vs {set(dec_filtered.keys())}"
            
        # Compare field values
        for field, orig_value in orig_filtered.items():
            dec_value = dec_filtered[field]
            assert orig_value == dec_value, \
                f"Field {field} differs in {context}: {orig_value} vs {dec_value}"