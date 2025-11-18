#!/usr/bin/env python3

from garmin_fit_sdk import Stream, Decoder

# Debug the filtered_bpm issue specifically
stream = Stream.from_file('tests/fits/HrmPluginTestActivity.fit')
decoder = Decoder(stream)
messages, errors = decoder.read(preserve_invalid_values=True, merge_heart_rates=False, expand_sub_fields=False, expand_components=False)

print("Looking for hr_mesgs and filtered_bpm field...")

if 'hr_mesgs' in messages:
    hr_messages = messages['hr_mesgs']
    print(f"Found {len(hr_messages)} HR messages")
    
    for i, hr_msg in enumerate(hr_messages):
        if 'filtered_bpm' in hr_msg:
            value = hr_msg['filtered_bpm']
            print(f"hr_mesgs[{i}] filtered_bpm: {value} (type: {type(value)})")
            if isinstance(value, list):
                print(f"  Array length: {len(value)}")
                print(f"  All values: {value}")
            else:
                print(f"  Scalar value: {value}")
else:
    print("No hr_mesgs found")