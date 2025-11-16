#!/usr/bin/env python3
"""Debug the HrmPluginTestActivity.fit encoding issue"""

import os
import tempfile
from garmin_fit_sdk import Decoder, Stream, Encoder

def debug_hrm_plugin_test():
    print("=== DEBUGGING HrmPluginTestActivity.fit ===")
    
    original_file = "tests/fits/HrmPluginTestActivity.fit"
    
    # Step 1: Decode original file and analyze
    original_stream = Stream.from_file(original_file)
    original_decoder = Decoder(original_stream)
    original_messages, original_errors = original_decoder.read()
    
    print(f"Original decoding: {len(original_errors)} errors")
    print(f"Message types: {list(original_messages.keys())}")
    
    for msg_type, messages in original_messages.items():
        print(f"  {msg_type}: {len(messages)} messages")
        if len(messages) > 0:
            # Check for None values in first few messages
            for i, msg in enumerate(messages[:3]):
                none_fields = [k for k, v in msg.items() if v is None]
                if none_fields:
                    print(f"    Message {i} has None fields: {none_fields}")
    
    # Step 2: Try encoding
    print(f"\n=== ENCODING ===")
    encoder = Encoder(original_messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        success = encoder.write_to_file(temp_path)
        print(f"Encoding result: {success}")
        
        if not success:
            print("Encoding failed!")
            return
        
        file_size = os.path.getsize(temp_path)
        print(f"Encoded file size: {file_size} bytes")
        
        # Step 3: Try decoding our file
        print(f"\n=== DECODING OUR FILE ===")
        try:
            new_stream = Stream.from_file(temp_path)
            new_decoder = Decoder(new_stream)
            
            # Basic checks
            new_stream.reset()
            print(f"Is FIT: {new_decoder.is_fit()}")
            
            new_stream.reset() 
            print(f"Integrity OK: {new_decoder.check_integrity()}")
            
            # Try decode
            new_stream.reset()
            new_messages, new_errors = new_decoder.read()
            
            print(f"Decode result: {len(new_errors)} errors")
            if new_errors:
                for error in new_errors:
                    print(f"  Error: {error}")
            else:
                print(f"✅ Decoded successfully: {list(new_messages.keys())}")
                
        except Exception as e:
            print(f"Exception during decode: {e}")
            import traceback
            traceback.print_exc()
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    debug_hrm_plugin_test()