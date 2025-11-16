#!/usr/bin/env python3
"""Get full traceback for the decode error"""

import tempfile
import traceback
from garmin_fit_sdk import Decoder, Stream, Encoder

def debug_with_traceback():
    print("=== DEBUG WITH FULL TRACEBACK ===")
    
    original_file = "tests/fits/HrmPluginTestActivity.fit"
    
    # Decode and encode
    original_stream = Stream.from_file(original_file)
    original_decoder = Decoder(original_stream)
    original_messages, _ = original_decoder.read()
    
    encoder = Encoder(original_messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    encoder.write_to_file(temp_path)
    
    # Now try decode with full traceback
    try:
        new_stream = Stream.from_file(temp_path)
        new_decoder = Decoder(new_stream)
        
        new_stream.reset()
        messages, errors = new_decoder.read()
        
        print(f"Errors: {len(errors)}")
        for error in errors:
            print(f"Error: {error}")
            print(f"Error type: {type(error)}")
            
    except Exception as e:
        print(f"Exception during decode: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == '__main__':
    debug_with_traceback()