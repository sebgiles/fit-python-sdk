#!/usr/bin/env python3
"""Debug specific field causing decode error"""

import tempfile
from garmin_fit_sdk import Decoder, Stream, Encoder

def debug_specific_field():
    print("=== DEBUGGING SPECIFIC DECODE FAILURE ===")
    
    original_file = "tests/fits/HrmPluginTestActivity.fit"
    
    # Decode original file
    original_stream = Stream.from_file(original_file)
    original_decoder = Decoder(original_stream)
    original_messages, original_errors = original_decoder.read()
    
    print(f"Original file decoding: {len(original_errors)} errors")
    
    # Encode it
    encoder = Encoder(original_messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    encoder.write_to_file(temp_path)
    
    # Now try to decode with better error handling to see where it fails
    try:
        new_stream = Stream.from_file(temp_path)
        new_decoder = Decoder(new_stream)
        
        # Let's manually step through the decoding to catch the exact failure point
        print("Checking basic properties...")
        new_stream.reset()
        print(f"Is FIT: {new_decoder.is_fit()}")
        
        new_stream.reset()
        print(f"Integrity: {new_decoder.check_integrity()}")
        
        # Try reading messages one by one to isolate the issue
        new_stream.reset()
        
        print("Starting decode...")
        messages = {}
        errors = []
        
        try:
            while True:
                message, error = new_decoder.read_next_message()
                if error:
                    errors.append(error)
                    print(f"Error reading message: {error}")
                    break
                if message is None:
                    break
                
                msg_type = message.name
                if msg_type not in messages:
                    messages[msg_type] = []
                messages[msg_type].append(message.get_values())
                
                print(f"Successfully read message: {msg_type}")
                
        except Exception as e:
            print(f"Exception during manual decode: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"Manual decode completed. Errors: {len(errors)}")
        
    except Exception as e:
        print(f"General exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_specific_field()