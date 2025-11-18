#!/usr/bin/env python3
import os
from garmin_fit_sdk import Stream, Decoder, Encoder

# Decode the original file
original_stream = Stream.from_file('tests/fits/HrmPluginTestActivity.fit')
original_decoder = Decoder(original_stream)

# Decode with non-expansion settings to match test
original_messages, original_errors = original_decoder.read(
    preserve_invalid_values=True,
    merge_heart_rates=False,
    expand_sub_fields=False,
    expand_components=False
)

print(f"Original decoding: {len(original_messages)} messages, {len(original_errors)} errors")

# Encode to a file
encoder = Encoder(original_messages)
output_file = 'debug_encoded.fit'
result = encoder.write_to_file(output_file)

print(f"Encoding result: {result}")
print(f"Output file exists: {os.path.exists(output_file)}")
print(f"Output file size: {os.path.getsize(output_file) if os.path.exists(output_file) else 0} bytes")

# Now let's manually inspect the file at byte 18095
if os.path.exists(output_file):
    with open(output_file, 'rb') as f:
        f.seek(18090)  # Read around the error location
        data = f.read(20)
        print(f"\nBytes around 18095: {data.hex()}")
        
        # Check individual bytes
        for i, byte in enumerate(data):
            print(f"  Byte {18090 + i}: {byte} (0x{byte:02x})")
            if 18090 + i == 18095:
                print(f"    *** ERROR BYTE {18095}: {byte} ***")