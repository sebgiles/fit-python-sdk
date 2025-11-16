#!/usr/bin/env python3
"""Test the new preserve_invalid_values decoder option"""

from garmin_fit_sdk import Decoder, Stream
from garmin_fit_sdk.encoder import Encoder
import tempfile
import os

def test_preserve_invalid_values():
    # Create test message with invalid value
    test_messages = {
        'file_id_mesgs': [{
            'type': 'activity',
            'manufacturer': 'garmin',
            'product': 1234,
            'serial_number': 987654321
        }],
        'device_settings_mesgs': [{
            'active_time_zone': 0,
            'time_mode': 'hour12',
            'auto_activity_detect': 2147483647,  # SINT32 invalid value
        }]
    }
    
    print("=== Testing preserve_invalid_values option ===")
    print("Original auto_activity_detect:", test_messages['device_settings_mesgs'][0]['auto_activity_detect'])
    
    # Encode
    encoder = Encoder(test_messages)
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp:
        temp_file = tmp.name
    
    try:
        success = encoder.write_to_file(temp_file)
        print(f"Encoding result: {success}")
        
        if success and os.path.exists(temp_file):
            print("\n=== Test 1: Normal decoder (should filter invalid values) ===")
            stream1 = Stream.from_file(temp_file)
            decoder1 = Decoder(stream1)
            decoded1, errors1 = decoder1.read(preserve_invalid_values=False)
            
            if 'device_settings_mesgs' in decoded1:
                device_settings1 = decoded1['device_settings_mesgs'][0]
                auto_detect1 = device_settings1.get('auto_activity_detect', 'NOT_FOUND')
                print(f"Normal decoder auto_activity_detect: {auto_detect1}")
            
            print("\n=== Test 2: Preserve invalid values (should keep invalid values) ===")
            stream2 = Stream.from_file(temp_file)
            decoder2 = Decoder(stream2)
            decoded2, errors2 = decoder2.read(preserve_invalid_values=True)
            
            if 'device_settings_mesgs' in decoded2:
                device_settings2 = decoded2['device_settings_mesgs'][0]
                auto_detect2 = device_settings2.get('auto_activity_detect', 'NOT_FOUND')
                print(f"Preserve invalid decoder auto_activity_detect: {auto_detect2}")
                
                if auto_detect2 == 2147483647:
                    print("✅ SUCCESS: Invalid value preserved!")
                else:
                    print("❌ FAILED: Invalid value not preserved")
        
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_preserve_invalid_values()