#!/usr/bin/env python3
"""Compare original vs encoded file headers and basic structure"""

import tempfile
import os
from garmin_fit_sdk import Decoder, Stream, Encoder

def compare_files():
    print("=== COMPARING FILE STRUCTURES ===")
    
    original_file = "tests/fits/HrmPluginTestActivity.fit"
    
    # Decode and re-encode
    original_stream = Stream.from_file(original_file)
    original_decoder = Decoder(original_stream)
    original_messages, _ = original_decoder.read()
    
    encoder = Encoder(original_messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    encoder.write_to_file(temp_path)
    
    # Compare file sizes
    original_size = os.path.getsize(original_file)
    encoded_size = os.path.getsize(temp_path)
    
    print(f"Original file size: {original_size} bytes")
    print(f"Encoded file size: {encoded_size} bytes")
    print(f"Size difference: {encoded_size - original_size} bytes")
    
    # Read first few bytes to compare headers
    with open(original_file, 'rb') as f:
        original_header = f.read(14)  # FIT file header is 14 bytes
    
    with open(temp_path, 'rb') as f:
        encoded_header = f.read(14)
    
    print(f"\nOriginal header: {original_header.hex()}")
    print(f"Encoded header:  {encoded_header.hex()}")
    print(f"Headers match: {original_header == encoded_header}")
    
    # Let's also check if there are any developer fields that might be problematic
    dev_field_count = 0
    unknown_field_count = 0
    
    for msg_type, messages in original_messages.items():
        for message in messages:
            for field_name in message.keys():
                if isinstance(field_name, int):
                    unknown_field_count += 1
                if 'developer' in str(field_name).lower():
                    dev_field_count += 1
    
    print(f"\nDeveloper fields: {dev_field_count}")
    print(f"Unknown fields (int keys): {unknown_field_count}")
    
    # Try a minimal decode of our file to see exactly where it fails
    try:
        new_stream = Stream.from_file(temp_path)
        new_decoder = Decoder(new_stream)
        
        # Check individual steps
        new_stream.reset()
        is_fit = new_decoder.is_fit()
        print(f"Our file is_fit(): {is_fit}")
        
        new_stream.reset()
        integrity = new_decoder.check_integrity()
        print(f"Our file check_integrity(): {integrity}")
        
        if is_fit and integrity:
            # Try decoding with simpler settings to avoid complex processing
            new_stream.reset()
            simple_messages, simple_errors = new_decoder.read(
                apply_scale_and_offset=False,
                convert_datetimes_to_dates=False,
                convert_types_to_strings=False,
                expand_sub_fields=False,
                expand_components=False,
                merge_heart_rates=False
            )
            
            print(f"Simple decode: {len(simple_errors)} errors")
            if simple_errors:
                for error in simple_errors:
                    print(f"  Error: {error}")
            else:
                print(f"✅ Simple decode successful!")
                
    except Exception as e:
        print(f"Exception during decode test: {e}")
    
    # Cleanup
    os.unlink(temp_path)

if __name__ == '__main__':
    compare_files()