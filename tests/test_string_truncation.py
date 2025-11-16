import pytest
from io import BytesIO
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.encoder import Encoder


class TestStringTruncation:
    
    def test_event_type_truncation_issue(self):
        """Test the event_type truncation from 'stop_all' to 'stop_'"""
        
        # Create a test message with stop_all event_type
        test_messages = {
            'event_mesgs': [{
                'timestamp': '2022-08-15T18:39:10Z',
                'event': 'timer', 
                'event_type': 'stop_all'
            }]
        }
        
        # Encode and decode
        encoder = Encoder(test_messages)
        encoded_bytes = encoder.write_to_bytes()
        
        bytes_io = BytesIO(encoded_bytes)
        stream = Stream.from_bytes_io(bytes_io)
        decoder = Decoder(stream)
        decoded_messages, errors = decoder.read()
        
        assert len(errors) == 0, f"Decoding errors: {errors}"
        assert 'event_mesgs' in decoded_messages
        
        decoded_event_type = decoded_messages['event_mesgs'][0]['event_type']
        print(f"Original: 'stop_all' (len: {len('stop_all')})")
        print(f"Decoded:  '{decoded_event_type}' (len: {len(decoded_event_type)})")
        
        # This should not truncate
        assert decoded_event_type == 'stop_all', f"event_type truncated: 'stop_all' -> '{decoded_event_type}'"
    
    def test_string_size_calculation_debug(self):
        """Debug string size calculation for event_type field"""
        
        # Test how the encoder determines field size for event_type
        test_messages = {
            'event_mesgs': [{
                'timestamp': '2022-08-15T18:39:10Z',
                'event': 'timer', 
                'event_type': 'stop_all'  # 8 chars + null = 9 bytes needed
            }]
        }
        
        # Debug the field definition creation
        original_determine_field_type = Encoder._determine_field_type_and_size
        
        def debug_field_type(self, field_profile, field_value):
            if isinstance(field_value, str) and 'stop_all' in field_value:
                print(f"DEBUG: Determining size for event_type")
                print(f"  Field profile: {field_profile}")
                print(f"  Field value: '{field_value}' (len: {len(field_value)})")
                result = original_determine_field_type(self, field_profile, field_value)
                print(f"  Result: base_type={result[0]}, size={result[1]}")
                return result
            return original_determine_field_type(self, field_profile, field_value)
        
        # Also debug string field writing  
        original_write_field_value = Encoder._write_field_value
        
        def debug_write_field_value(self, value, size, base_type, field_profile):
            if isinstance(value, str) and 'stop_all' in value:
                print(f"DEBUG: Writing string field")
                print(f"  Value: '{value}' (len: {len(value)})")
                print(f"  Size: {size}, Base type: {base_type}")
                print(f"  Profile name: {field_profile.get('name', 'unknown')}")
            return original_write_field_value(self, value, size, base_type, field_profile)
        
        # Monkey patch
        Encoder._determine_field_type_and_size = debug_field_type
        Encoder._write_field_value = debug_write_field_value
        
        try:
            encoder = Encoder(test_messages)
            encoded_bytes = encoder.write_to_bytes()
            
            bytes_io = BytesIO(encoded_bytes)
            stream = Stream.from_bytes_io(bytes_io)
            decoder = Decoder(stream)
            decoded_messages, errors = decoder.read()
            
            decoded_event_type = decoded_messages['event_mesgs'][0]['event_type']
            print(f"Final result: '{decoded_event_type}'")
            
        finally:
            # Restore
            Encoder._determine_field_type_and_size = original_determine_field_type
            Encoder._write_field_value = original_write_field_value