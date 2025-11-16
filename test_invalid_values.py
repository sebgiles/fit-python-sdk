#!/usr/bin/env python3
"""Test how encoder handles fields with invalid values"""

from garmin_fit_sdk import Decoder, Stream
from garmin_fit_sdk.encoder import Encoder
import tempfile
import os

def test_invalid_value_handling():
    # Create a test message with an invalid value
    test_messages = {
        'file_id_mesgs': [{
            'type': 'activity',
            'manufacturer': 'garmin',
            'product': 1234,
            'serial_number': 987654321
        }],
        'device_settings_mesgs': [{
            # Normal fields
            'active_time_zone': 0,
            'time_mode': 'hour12',
            # Field with invalid value
            'auto_activity_detect': 2147483647,  # SINT32 invalid value
        }]
    }
    
    print("=== Testing invalid value handling ===")
    print("Original device_settings auto_activity_detect:", test_messages['device_settings_mesgs'][0]['auto_activity_detect'])
    
    # Encode
    encoder = Encoder(test_messages)
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp:
        temp_file = tmp.name
    
    try:
        success = encoder.write_to_file(temp_file)
        print(f"Encoding result: {success}")
        
        if success and os.path.exists(temp_file):
            # Decode back
            stream = Stream.from_file(temp_file)
            decoder = Decoder(stream)
            decoded_messages, errors = decoder.read()
            
            print(f"Decoding errors: {len(errors)}")
            
            if 'device_settings_mesgs' in decoded_messages:
                device_settings = decoded_messages['device_settings_mesgs'][0]
                print("Decoded device_settings fields:", list(device_settings.keys()))
                print("Decoded auto_activity_detect:", device_settings.get('auto_activity_detect', 'NOT_FOUND'))
                
                # Also check all field values
                for field, value in device_settings.items():
                    if value == 2147483647:
                        print(f"Found value 2147483647 in field: {field}")
        
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_invalid_value_handling()