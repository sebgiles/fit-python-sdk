#!/usr/bin/env python3
from garmin_fit_sdk import Stream, Decoder

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

# Look at the message structure
for msg_type, messages in original_messages.items():
    print(f"\nMessage type: {msg_type} ({len(messages)} messages)")
    if msg_type == 'hr_mesgs' and len(messages) > 0:
        print(f"  Sample HR message keys: {list(messages[0].keys())}")
        print(f"  Sample HR message: {messages[0]}")
        
        # Look for filtered_bpm in first few messages
        for i, msg in enumerate(messages[:5]):
            if 'filtered_bpm' in msg:
                filtered_bpm = msg['filtered_bpm']
                print(f"    HR message {i}: filtered_bpm = {filtered_bpm}, type = {type(filtered_bpm)}")
                
        break