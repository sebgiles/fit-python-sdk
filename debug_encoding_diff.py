#!/usr/bin/env python3
"""Debug specific encoding differences"""

import os
import tempfile
from garmin_fit_sdk import Decoder, Stream, Encoder

def compare_small_file():
    """Compare with the smallest test file to minimize complexity"""
    original_file = "tests/fits/ActivityDevFields.fit"
    
    print("=== SMALL FILE COMPARISON ===")
    
    # Decode original
    stream = Stream.from_file(original_file)
    decoder = Decoder(stream)
    original_messages, errors = decoder.read(
        expand_components=False,
        expand_sub_fields=False, 
        merge_heart_rates=False
    )
    
    if errors:
        print(f"Original decode errors: {errors}")
        return
    
    print(f"Original messages structure:")
    for msg_type, msgs in original_messages.items():
        print(f"  {msg_type}: {len(msgs)} messages")
        if len(msgs) > 0:
            first_msg = msgs[0]
            print(f"    First message fields: {sorted(first_msg.keys())}")
    
    # Show first few record messages in detail
    if 'record_mesgs' in original_messages:
        print(f"\nFirst 3 record messages:")
        for i, record in enumerate(original_messages['record_mesgs'][:3]):
            print(f"  Record {i}: {len(record)} fields")
            for field, value in sorted(record.items()):
                print(f"    {field}: {value} ({type(value).__name__})")
    
    # Encode with our encoder
    encoder = Encoder(original_messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        success = encoder.write_to_file(temp_path)
        print(f"\nEncoding success: {success}")
        
        # Compare file sizes
        orig_size = os.path.getsize(original_file)
        encoded_size = os.path.getsize(temp_path)
        print(f"Original size: {orig_size}, Encoded size: {encoded_size}, Diff: {encoded_size - orig_size}")
        
        # Compare binary structure in detail
        with open(original_file, 'rb') as f:
            orig_data = f.read()
        
        with open(temp_path, 'rb') as f:
            encoded_data = f.read()
        
        print(f"\nHeader comparison:")
        print(f"Original: {orig_data[:14].hex()}")
        print(f"Encoded:  {encoded_data[:14].hex()}")
        
        print(f"\nFirst 50 data bytes:")
        print(f"Original: {orig_data[14:64].hex()}")
        print(f"Encoded:  {encoded_data[14:64].hex()}")
        
        # Find first difference
        min_len = min(len(orig_data), len(encoded_data))
        for i in range(min_len):
            if orig_data[i] != encoded_data[i]:
                print(f"\nFirst difference at byte {i}:")
                print(f"  Original: {orig_data[i]:02x}")
                print(f"  Encoded:  {encoded_data[i]:02x}")
                
                # Show context around difference
                start = max(0, i-10)
                end = min(len(orig_data), i+10)
                print(f"  Context orig[{start}:{end}]: {orig_data[start:end].hex()}")
                print(f"  Context enc[{start}:{end}]: {encoded_data[start:end].hex()}")
                break
        
        # Try to decode our encoded file
        print(f"\n=== DECODING OUR ENCODED FILE ===")
        try:
            enc_stream = Stream.from_file(temp_path)
            enc_decoder = Decoder(enc_stream)
            
            enc_messages, enc_errors = enc_decoder.read(
                expand_components=False,
                expand_sub_fields=False,
                merge_heart_rates=False
            )
            
            if enc_errors:
                print(f"Encoded file decode errors: {enc_errors}")
            else:
                print(f"Encoded file decoded successfully!")
                for msg_type, msgs in enc_messages.items():
                    print(f"  {msg_type}: {len(msgs)} messages")
        
        except Exception as e:
            print(f"Exception decoding our file: {e}")
            import traceback
            traceback.print_exc()
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    compare_small_file()