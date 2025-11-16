#!/usr/bin/env python3
"""Test whether invalid values are encoded but filtered by decoder"""

from garmin_fit_sdk import Decoder, Stream
from garmin_fit_sdk.encoder import Encoder
import tempfile
import os

def test_binary_content():
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
    
    print("=== Testing binary content for invalid values ===")
    
    # Encode
    encoder = Encoder(test_messages)
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp:
        temp_file = tmp.name
    
    try:
        success = encoder.write_to_file(temp_file)
        print(f"Encoding result: {success}")
        
        if success and os.path.exists(temp_file):
            file_size = os.path.getsize(temp_file)
            print(f"Encoded file size: {file_size} bytes")
            
            # Read the binary content
            with open(temp_file, 'rb') as f:
                binary_data = f.read()
            
            # Search for the 4-byte representation of 2147483647
            # 2147483647 = 0x7FFFFFFF in little-endian = FF FF FF 7F
            invalid_bytes = (2147483647).to_bytes(4, 'little')
            print(f"Looking for bytes: {invalid_bytes.hex()}")
            
            if invalid_bytes in binary_data:
                positions = []
                start = 0
                while True:
                    pos = binary_data.find(invalid_bytes, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1
                print(f"✅ Found invalid value at positions: {positions}")
            else:
                print("❌ Invalid value NOT found in binary data")
            
            # Now test decoder with different approaches
            print("\n=== Testing different decoder approaches ===")
            
            # Approach 1: Normal decoder
            stream1 = Stream.from_file(temp_file)
            decoder1 = Decoder(stream1)
            decoded1, errors1 = decoder1.read()
            
            print(f"Normal decoder: {len(errors1)} errors")
            if 'device_settings_mesgs' in decoded1:
                dev_settings = decoded1['device_settings_mesgs'][0]
                print(f"Fields found: {list(dev_settings.keys())}")
                auto_detect = dev_settings.get('auto_activity_detect', 'NOT_FOUND')
                print(f"auto_activity_detect: {auto_detect}")
            
            # Approach 2: Check raw message content before full processing
            stream2 = Stream.from_file(temp_file)
            decoder2 = Decoder(stream2)
            
            # Try to access lower-level decoder features if available
            print("\n=== Checking if decoder has options to preserve invalid values ===")
            print("Decoder attributes:", [attr for attr in dir(decoder2) if not attr.startswith('_')])
        
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_binary_content()