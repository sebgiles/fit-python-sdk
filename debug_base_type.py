#!/usr/bin/env python3
from garmin_fit_sdk import Stream, Decoder, BASE_TYPE_DEFINITIONS

# Check what base types are valid
print("Valid FIT base types:")
for base_type_val, base_type_info in BASE_TYPE_DEFINITIONS.items():
    print(f"  {base_type_val}: {base_type_info}")

print("\nDecoding encoded file to find invalid base type...")
stream = Stream.from_file('/tmp/tmp57dwtluw/encoded_HrmPluginTestActivity.fit')
decoder = Decoder(stream)

try:
    messages, errors = decoder.read()
    print(f"Decoding successful: {len(messages)} messages, {len(errors)} errors")
except Exception as e:
    print(f"Decoding failed: {e}")
    
    # Manual investigation of the file at byte 18095
    with open('/tmp/tmp57dwtluw/encoded_HrmPluginTestActivity.fit', 'rb') as f:
        f.seek(18090)  # Read around the error location
        data = f.read(20)
        print(f"Bytes around 18095: {data.hex()}")
        
        # Check individual bytes
        for i, byte in enumerate(data):
            print(f"  Byte {18090 + i}: {byte} (0x{byte:02x})")
            if 18090 + i == 18095:
                print(f"    *** ERROR BYTE {18095}: {byte} ***")
                if byte in BASE_TYPE_DEFINITIONS:
                    print(f"    This is a valid base type: {BASE_TYPE_DEFINITIONS[byte]}")
                else:
                    print(f"    This is NOT a valid base type!")