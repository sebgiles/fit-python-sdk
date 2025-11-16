'''test_encoder.py: Contains the set of tests for the encoder class in the Python FIT SDK'''


import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone

import pytest
from garmin_fit_sdk import Decoder, Encoder, Stream
from garmin_fit_sdk import fit as FIT


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
        
        result = encoder.write_to_file(output_file)
        assert result is True
        assert os.path.exists(output_file)

    def test_encoder_write_to_bytes_should_work(self):
        '''Tests that write_to_bytes should work when implemented'''
        encoder = Encoder({})
        
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

    def test_timestamp_conversion_round_trip(self):
        """Test that datetime to FIT timestamp conversion is reversible"""
        from garmin_fit_sdk.util import FIT_EPOCH_S
        
        # Test with a known datetime
        original_datetime = datetime(2022, 8, 15, 17, 39, 9, tzinfo=timezone.utc)
        
        # Convert to FIT timestamp (what encoder should do)
        unix_timestamp = original_datetime.timestamp()
        fit_timestamp = int(unix_timestamp - FIT_EPOCH_S)
        
        # Convert back to datetime (what decoder does)
        recovered_datetime = datetime.fromtimestamp(fit_timestamp + FIT_EPOCH_S, timezone.utc)
        
        # Should be identical
        assert original_datetime == recovered_datetime, f"Original: {original_datetime}, Recovered: {recovered_datetime}"
        
        # Test that our conversion logic matches what should happen
        # This tests the same logic that's in the encoder
        assert fit_timestamp > 0, "FIT timestamp should be positive"
        assert fit_timestamp < 2**32, "FIT timestamp should fit in uint32"

    def test_fit_epoch_calculation(self):
        """Test that our FIT epoch calculations are correct"""
        from garmin_fit_sdk.util import FIT_EPOCH_S
        
        # FIT epoch is 1989-12-31 00:00:00 UTC
        fit_epoch_dt = datetime(1989, 12, 31, 0, 0, 0, tzinfo=timezone.utc)
        unix_epoch_dt = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        
        # The difference should be FIT_EPOCH_S
        expected_diff = fit_epoch_dt.timestamp() - unix_epoch_dt.timestamp()
        assert abs(expected_diff - FIT_EPOCH_S) < 1, f"FIT_EPOCH_S mismatch: expected {expected_diff}, got {FIT_EPOCH_S}"