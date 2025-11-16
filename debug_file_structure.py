#!/usr/bin/env python3
"""Debug script to compare original vs encoded FIT file structure"""

import os
import tempfile
from garmin_fit_sdk import Decoder, Stream, Encoder

def analyze_fit_file(file_path, label):
    """Analyze the structure of a FIT file"""
    print(f"\n=== {label} ===")
    
    if not os.path.exists(file_path):
        print(f"File does not exist: {file_path}")
        return None
    
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size} bytes")
    
    # Read raw bytes to examine header
    with open(file_path, 'rb') as f:
        header = f.read(14)  # FIT header is 14 bytes
        print(f"Header (14 bytes): {header.hex()}")
        
        if len(header) >= 14:
            header_size = header[0]
            protocol_version = header[1]
            profile_version = int.from_bytes(header[2:4], 'little')
            data_size = int.from_bytes(header[4:8], 'little')
            fit_signature = header[8:12]
            crc = int.from_bytes(header[12:14], 'little') if header_size >= 14 else None
            
            print(f"  Header size: {header_size}")
            print(f"  Protocol version: {protocol_version}")
            print(f"  Profile version: {profile_version}")
            print(f"  Data size: {data_size}")
            print(f"  FIT signature: {fit_signature} ({''.join(chr(b) for b in fit_signature)})")
            if crc is not None:
                print(f"  Header CRC: {crc:04x}")
    
    # Try to analyze with decoder
    try:
        stream = Stream.from_file(file_path)
        decoder = Decoder(stream)
        
        # Check basic validity
        stream.reset()
        is_fit = decoder.is_fit()
        print(f"Is valid FIT: {is_fit}")
        
        stream.reset()
        integrity_ok = decoder.check_integrity()
        print(f"Integrity check: {integrity_ok}")
        
        # Try to decode
        stream.reset()
        messages, errors = decoder.read(
            expand_components=False,
            expand_sub_fields=False,
            merge_heart_rates=False
        )
        
        if errors:
            print(f"Decode errors: {errors}")
            return None
        else:
            print(f"Decode successful: {len(messages)} message types")
            for msg_type, msg_list in messages.items():
                print(f"  {msg_type}: {len(msg_list)} messages")
            
            return messages
            
    except Exception as e:
        print(f"Exception during decode: {e}")
        return None

def main():
    # Test with a simple original file first
    original_file = "tests/fits/WithGearChangeData.fit"
    
    print("Analyzing original vs encoded file structure")
    
    # Analyze original
    original_messages = analyze_fit_file(original_file, "ORIGINAL FILE")
    
    if original_messages is None:
        print("Cannot proceed - original file analysis failed")
        return
    
    # Encode it
    print(f"\n=== ENCODING ===")
    encoder = Encoder(original_messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        success = encoder.write_to_file(temp_path)
        print(f"Encoding result: {success}")
        
        if success:
            # Analyze encoded file
            encoded_messages = analyze_fit_file(temp_path, "ENCODED FILE")
            
            # Compare raw file structure
            print(f"\n=== BINARY COMPARISON ===")
            
            with open(original_file, 'rb') as f:
                orig_data = f.read()
            
            with open(temp_path, 'rb') as f:
                encoded_data = f.read()
            
            print(f"Original size: {len(orig_data)} bytes")
            print(f"Encoded size: {len(encoded_data)} bytes")
            
            # Compare headers
            print(f"Headers match: {orig_data[:14] == encoded_data[:14]}")
            
            if orig_data[:14] != encoded_data[:14]:
                print(f"Original header: {orig_data[:14].hex()}")
                print(f"Encoded header:  {encoded_data[:14].hex()}")
            
            # Look at first few data bytes after header
            print(f"First 20 data bytes:")
            print(f"Original: {orig_data[14:34].hex()}")
            print(f"Encoded:  {encoded_data[14:34].hex()}")
            
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    main()