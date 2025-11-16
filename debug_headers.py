#!/usr/bin/env python3
"""Decode FIT file headers to understand the differences"""

import struct
import tempfile
from garmin_fit_sdk import Decoder, Stream, Encoder

def decode_fit_header(header_bytes):
    """Decode a 14-byte FIT header"""
    print(f"Header bytes: {header_bytes.hex()}")
    
    # FIT header structure:
    # 0: header_size (1 byte)
    # 1: protocol_version (1 byte) 
    # 2-3: profile_version (2 bytes, little endian)
    # 4-7: data_size (4 bytes, little endian)
    # 8-11: data_type ('.FIT', 4 bytes)
    # 12-13: crc (2 bytes, little endian) - optional
    
    header_size = header_bytes[0]
    protocol_version = header_bytes[1] 
    profile_version = struct.unpack('<H', header_bytes[2:4])[0]
    data_size = struct.unpack('<L', header_bytes[4:8])[0]
    data_type = header_bytes[8:12].decode('ascii')
    
    print(f"  Header size: {header_size}")
    print(f"  Protocol version: {protocol_version}")
    print(f"  Profile version: {profile_version}")
    print(f"  Data size: {data_size}")
    print(f"  Data type: '{data_type}'")
    
    if header_size >= 14:
        crc = struct.unpack('<H', header_bytes[12:14])[0]
        print(f"  CRC: 0x{crc:04x}")
    else:
        print(f"  CRC: Not present (header size {header_size})")

def analyze_headers():
    print("=== ANALYZING FIT HEADERS ===")
    
    original_file = "tests/fits/HrmPluginTestActivity.fit"
    
    # Get original header
    with open(original_file, 'rb') as f:
        original_header = f.read(14)
    
    print("ORIGINAL FILE HEADER:")
    decode_fit_header(original_header)
    
    # Decode and encode
    original_stream = Stream.from_file(original_file)
    original_decoder = Decoder(original_stream)
    original_messages, _ = original_decoder.read()
    
    encoder = Encoder(original_messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    encoder.write_to_file(temp_path)
    
    # Get encoded header
    with open(temp_path, 'rb') as f:
        encoded_header = f.read(14)
    
    print("\nOUR ENCODED FILE HEADER:")
    decode_fit_header(encoded_header)
    
    print("\nHEADER COMPARISON:")
    for i in range(14):
        if original_header[i] != encoded_header[i]:
            print(f"  Byte {i}: {original_header[i]:02x} -> {encoded_header[i]:02x}")

if __name__ == '__main__':
    analyze_headers()