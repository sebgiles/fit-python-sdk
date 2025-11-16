'''test_encoder.py: Contains the set of tests for the encoder class in the Python FIT SDK'''

###########################################################################################
# Copyright 2025 Garmin International, Inc.
# Licensed under the Flexible and Interoperable Data Transfer (FIT) Protocol License; you
# may not use this file except in compliance with the Flexible and Interoperable Data
# Transfer (FIT) Protocol License.
###########################################################################################


import os
import tempfile
from pathlib import Path

import pytest
from garmin_fit_sdk import Decoder, Encoder, Stream


class TestEncoder:
    '''Set of tests to verify that the encoder class correctly encodes and round-trips FIT files.'''

    @pytest.fixture
    def test_fit_files(self):
        '''Fixture that provides paths to test FIT files'''
        test_files_dir = Path(__file__).parent / "fits"
        fit_files = []
        
        # Collect all .fit files in the test directory
        for fit_file in test_files_dir.glob("*.fit"):
            if fit_file.is_file():
                fit_files.append(str(fit_file))
        
        return fit_files

    @pytest.fixture
    def temp_dir(self):
        '''Fixture that provides a temporary directory for test files'''
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir

    def test_encoder_constructor_with_none_messages(self):
        '''Tests that encoder constructor raises error with None messages'''
        with pytest.raises(RuntimeError, match="FIT Runtime Error messages parameter is None"):
            Encoder(None)

    def test_encoder_constructor_with_empty_messages(self):
        '''Tests that encoder constructor accepts empty messages dict'''
        encoder = Encoder({})
        assert encoder is not None
        assert encoder._messages == {}

    def test_encoder_constructor_with_valid_messages(self):
        '''Tests that encoder constructor accepts valid messages dict'''
        messages = {
            'file_id_mesgs': [{'type': 'activity', 'manufacturer': 'garmin'}],
            'record_mesgs': []
        }
        encoder = Encoder(messages)
        assert encoder is not None
        assert encoder._messages == messages

    def test_encoder_write_to_file_should_work(self, temp_dir):
        '''Tests that write_to_file should work when implemented'''
        encoder = Encoder({})
        output_file = os.path.join(temp_dir, "test_output.fit")
        
        # TDD: This should work when implemented, for now it will fail
        result = encoder.write_to_file(output_file)
        assert result is True
        assert os.path.exists(output_file)

    def test_encoder_write_to_bytes_should_work(self):
        '''Tests that write_to_bytes should work when implemented'''
        encoder = Encoder({})
        
        # TDD: This should work when implemented, for now it will fail
        result = encoder.write_to_bytes()
        assert isinstance(result, bytearray)
        assert len(result) > 0

    @pytest.mark.parametrize("fit_file", [
        "tests/fits/ActivityDevFields.fit",
        "tests/fits/HrmPluginTestActivity.fit", 
        "tests/fits/WithGearChangeData.fit"
    ])
    def test_decode_original_file(self, fit_file):
        '''Tests that we can successfully decode the original FIT files'''
        if not os.path.exists(fit_file):
            pytest.skip(f"Test file {fit_file} not found")
            
        # Step 1: Read and validate original file
        stream = Stream.from_file(fit_file)
        decoder = Decoder(stream)
        
        # Verify file integrity
        stream.reset()
        assert decoder.is_fit(), f"File {fit_file} is not a valid FIT file"
        
        stream.reset()
        assert decoder.check_integrity(), f"File {fit_file} failed integrity check"
        
        # Decode the file
        stream.reset()
        messages, errors = decoder.read()
        
        # Verify decoding was successful
        assert len(errors) == 0, f"Decoding errors: {errors}"
        assert isinstance(messages, dict), "Messages should be a dictionary"
        assert len(messages) > 0, "Messages should not be empty"
        
        # Verify essential message structure
        assert 'file_id_mesgs' in messages, "Missing file_id_mesgs"
        assert len(messages['file_id_mesgs']) > 0, "file_id_mesgs should not be empty"

    @pytest.mark.parametrize("fit_file", [
        "tests/fits/ActivityDevFields.fit",
        "tests/fits/HrmPluginTestActivity.fit", 
        "tests/fits/WithGearChangeData.fit"
    ])
    def test_round_trip_encoding(self, fit_file, temp_dir):
        '''
        Test complete round-trip encoding: decode -> encode -> decode -> compare.
        This is the core TDD test that drives encoder implementation.
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
        
        # Step 2: Encode to new file - TDD: This should work when implemented
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

    def test_message_structure_validation(self):
        '''Tests validation of message structure that will be passed to encoder'''
        # Test various message structures that the encoder should handle
        
        # Valid basic message structure
        valid_messages = {
            'file_id_mesgs': [{
                'type': 'activity',
                'manufacturer': 'garmin',
                'product': 1234,
                'serial_number': 5678,
                'time_created': 1000000000
            }],
            'record_mesgs': [{
                'timestamp': 1000000001,
                'position_lat': 123456789,
                'position_long': 987654321,
                'distance': 1000,
                'speed': 5000
            }]
        }
        
        encoder = Encoder(valid_messages)
        assert encoder._messages == valid_messages
        
        # Test with empty message lists (should be valid)
        empty_messages = {
            'file_id_mesgs': [],
            'record_mesgs': []
        }
        
        encoder_empty = Encoder(empty_messages)
        assert encoder_empty._messages == empty_messages

    def test_message_data_types_validation(self):
        '''Tests that encoder handles various data types correctly'''
        
        # Create messages with different data types
        mixed_type_messages = {
            'file_id_mesgs': [{
                'type': 'activity',                    # string/enum
                'manufacturer': 'garmin',             # string/enum  
                'product': 1234,                      # integer
                'serial_number': 5678,                # integer
                'time_created': 1000000000,           # timestamp
                'number': 12.5                        # float (if supported)
            }],
            'device_info_mesgs': [{
                'device_index': 0,                    # integer
                'device_type': 120,                   # integer
                'manufacturer': 'garmin',             # string
                'product': 'edge_1030',               # string
                'software_version': 4.20,             # float
                'battery_voltage': 3.8                # float
            }]
        }
        
        encoder = Encoder(mixed_type_messages)
        assert encoder._messages == mixed_type_messages

    @pytest.mark.parametrize("decode_options", [
        # Test with different decoder options to ensure encoder can handle various message formats
        {
            'apply_scale_and_offset': True,
            'convert_datetimes_to_dates': True,
            'convert_types_to_strings': True,
            'expand_sub_fields': True,
            'expand_components': True
        },
        {
            'apply_scale_and_offset': False,
            'convert_datetimes_to_dates': False, 
            'convert_types_to_strings': False,
            'expand_sub_fields': False,
            'expand_components': False
        }
    ])
    def test_encoder_with_different_decode_options(self, decode_options):
        '''Tests that encoder can handle messages decoded with different options'''
        
        # For now, we'll test with simulated data since we don't have real encoder yet
        # This test ensures the encoder can accept different message formats
        
        # Simulate messages as they would appear with different decode options
        if decode_options['convert_types_to_strings']:
            test_messages = {
                'file_id_mesgs': [{
                    'type': 'activity',           # string format
                    'manufacturer': 'garmin'      # string format
                }]
            }
        else:
            test_messages = {
                'file_id_mesgs': [{
                    'type': 4,                    # numeric format
                    'manufacturer': 1             # numeric format  
                }]
            }
            
        encoder = Encoder(test_messages)
        assert encoder._messages == test_messages

    def test_file_size_and_integrity_expectations(self):
        '''Tests expectations for encoded file size and integrity'''
        
        # This test documents what we expect from the encoder once implemented
        large_messages = {
            'file_id_mesgs': [{'type': 'activity', 'manufacturer': 'garmin'}],
            'record_mesgs': [
                {
                    'timestamp': 1000000000 + i,
                    'position_lat': 123456789 + i*10,
                    'position_long': 987654321 + i*10, 
                    'distance': i * 100,
                    'speed': i * 50
                } for i in range(1000)  # 1000 record messages
            ]
        }
        
        encoder = Encoder(large_messages)
        assert len(encoder._messages['record_mesgs']) == 1000
        
        # TODO: Once encoder is implemented, verify:
        # - Encoded file size is reasonable (not too large, not too small)
        # - File has proper FIT header
        # - File has proper CRC
        # - File can be decoded by decoder

    def _compare_messages_deep(self, original, decoded, ignore_fields=None):
        '''
        Helper method to deeply compare two message dictionaries.
        Will be used for round-trip testing once encoder is implemented.
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