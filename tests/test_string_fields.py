'''test_string_fields.py: Tests for string field encoding/decoding'''

import pytest
from garmin_fit_sdk import Decoder, Stream, Encoder
from io import BytesIO


class TestStringFields:
    def test_string_field_preservation(self):
        """Test that string fields are preserved during encoding"""
        # Create test messages with string fields
        test_messages = {
            'device_info_mesgs': [{
                'manufacturer': 'development',
                'product': 0,
                'product_name': 'Test Product',  # String field that should be preserved
                'software_version': 'v1.0',
                'serial_number': 12345
            }]
        }
        
        print(f"\n=== DEBUG: String Field Test ===")
        print(f"Input message: {test_messages['device_info_mesgs'][0]}")
        
        # Encode
        encoder = Encoder(test_messages)
        print(f"Encoder created successfully")
        
        # Check what field definitions were created
        if hasattr(encoder, '_local_mesg_defs'):
            print(f"Local message definitions: {encoder._local_mesg_defs}")
        
        encoded_bytes = encoder.write_to_bytes()
        print(f"Encoded {len(encoded_bytes)} bytes")
        
        # Decode
        bytes_io = BytesIO(encoded_bytes)
        stream = Stream.from_bytes_io(bytes_io)
        decoder = Decoder(stream)
        decoded_messages, errors = decoder.read()
        
        print(f"Decoding errors: {errors}")
        print(f"Decoded message types: {list(decoded_messages.keys())}")
        
        # Check that string field is preserved
        assert len(errors) == 0, f"Decoding errors: {errors}"
        assert 'device_info_mesgs' in decoded_messages
        assert len(decoded_messages['device_info_mesgs']) > 0
        
        decoded_msg = decoded_messages['device_info_mesgs'][0]
        print(f"Original: {test_messages['device_info_mesgs'][0].keys()}")
        print(f"Decoded: {decoded_msg.keys()}")
        print(f"Decoded message: {decoded_msg}")
        
        # The critical test - string field should be preserved
        assert 'product_name' in decoded_msg, f"product_name missing from decoded message: {decoded_msg}"
        assert decoded_msg['product_name'] == 'Test Product'

    def test_garmin_product_field(self):
        """Test garmin_product string field specifically"""
        test_messages = {
            'file_id_mesgs': [{
                'manufacturer': 'garmin',
                'product': 3843,
                'garmin_product': 'edge_1040',  # This field gets dropped
                'type': 'activity'
            }]
        }
        
        encoder = Encoder(test_messages)
        encoded_bytes = encoder.write_to_bytes()
        
        bytes_io = BytesIO(encoded_bytes)
        stream = Stream.from_bytes_io(bytes_io)
        decoder = Decoder(stream)
        decoded_messages, errors = decoder.read()
        
        assert len(errors) == 0
        decoded_msg = decoded_messages['file_id_mesgs'][0]
        
        print(f"Original keys: {test_messages['file_id_mesgs'][0].keys()}")
        print(f"Decoded keys: {decoded_msg.keys()}")
        
        assert 'garmin_product' in decoded_msg, f"garmin_product missing: {decoded_msg}"
        assert decoded_msg['garmin_product'] == 'edge_1040'