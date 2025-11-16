#!/usr/bin/env python3
"""Test encoding/decoding of specific problematic fields"""

import tempfile
from garmin_fit_sdk import Decoder, Stream, Encoder

def test_specific_problem():
    print("=== TESTING SPECIFIC PROBLEM FIELDS ===")
    
    # Create a simple test with just the problematic field patterns
    test_messages = {
        'device_settings_mesgs': [
            {
                104: [0, 24, 8, 7, 2, 3, 14, 13, 16, 1, 23, 26, 29, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
            }
        ]
    }
    
    print("Creating encoder with problematic array field...")
    encoder = Encoder(test_messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    print("Encoding...")
    success = encoder.write_to_file(temp_path)
    print(f"Encoding success: {success}")
    
    if success:
        print("Attempting decode...")
        try:
            new_stream = Stream.from_file(temp_path)
            new_decoder = Decoder(new_stream)
            
            new_stream.reset()
            print(f"Is FIT: {new_decoder.is_fit()}")
            
            new_stream.reset()
            print(f"Integrity: {new_decoder.check_integrity()}")
            
            new_stream.reset()
            messages, errors = new_decoder.read()
            
            print(f"Decode result: {len(errors)} errors")
            if errors:
                for error in errors:
                    print(f"  Error: {error}")
            else:
                print("✅ Success!")
                print(f"Decoded messages: {list(messages.keys())}")
                
        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_specific_problem()