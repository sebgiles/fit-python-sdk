#!/usr/bin/env python3
from garmin_fit_sdk import Stream, Decoder, BASE_TYPE_DEFINITIONS

# Now try to decode the file to see exactly where the error occurs
try:
    stream = Stream.from_file('debug_encoded.fit')
    decoder = Decoder(stream)
    messages, errors = decoder.read()
    print(f"Decoding successful: {len(messages)} messages, {len(errors)} errors")
    if errors:
        print(f"Errors: {errors}")
except Exception as e:
    print(f"Decoding failed: {e}")

# Check valid base types
print(f"\nValid base types: {list(BASE_TYPE_DEFINITIONS.keys())}")
print(f"Base type 71 is valid: {71 in BASE_TYPE_DEFINITIONS}")
print(f"Base type 71 hex: 0x{71:02x}")

# Let's also compare with the original file structure at this location
print("\nOriginal file at same location:")
with open('tests/fits/HrmPluginTestActivity.fit', 'rb') as f:
    f.seek(18090)
    data = f.read(20)
    print(f"Original bytes around 18095: {data.hex()}")
    
    for i, byte in enumerate(data):
        print(f"  Byte {18090 + i}: {byte} (0x{byte:02x})")
        if 18090 + i == 18095:
            print(f"    *** ORIGINAL BYTE {18095}: {byte} ***")