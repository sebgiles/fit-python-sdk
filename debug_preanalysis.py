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

# Create encoder to test pre-analysis
encoder = Encoder(original_messages)

# Test the pre-analysis method directly
all_messages = []
for messages in encoder._messages.values():
    all_messages.extend(messages)

field_defs = encoder._analyze_field_types_across_messages(all_messages)

# Look for filtered_bpm field issues
print(f"\nField type analysis results:")
for field_name, analysis in field_defs.items():
    if field_name == 'filtered_bpm':
        print(f"  Field {field_name}:")
        print(f"    is_array: {analysis['is_array']}")
        if analysis['is_array']:
            print(f"    array_size: {analysis['array_size']}")
        print(f"    sample_values (first 3): {analysis['sample_values'][:3]}")
        
print(f"\nTotal field definitions analyzed: {len(field_defs)}")

# Look at HR messages specifically
hr_messages = [msg for msg in all_messages if msg.get('mesg_num') == 132]  # HR message type
print(f"\nFound {len(hr_messages)} HR messages")

for i, msg in enumerate(hr_messages[:5]):  # Show first 5
    if 'fields' in msg and 104 in msg['fields']:
        filtered_bpm = msg['fields'][104]
        print(f"  HR message {i}: filtered_bpm = {filtered_bpm}, type = {type(filtered_bpm)}")
    else:
        print(f"  HR message {i}: no filtered_bpm field")