#!/usr/bin/env python3

import sys
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder

def debug_field_usage():
    fit_file = "tests/fits/WithGearChangeData.fit"
    
    # Decode the file
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    stream.reset()
    messages, errors = decoder.read()
    
    # Get record messages
    if 'record_mesgs' in messages:
        records = messages['record_mesgs']
        print(f"Total record messages: {len(records)}")
        
        # Count field usage
        field_usage = {}
        for message in records:
            for field_name in message.keys():
                # Skip numeric field IDs and None values
                if not isinstance(field_name, int) and message[field_name] is not None:
                    field_usage[field_name] = field_usage.get(field_name, 0) + 1
        
        print(f"\nField usage statistics:")
        min_usage = max(1, len(records) // 10)
        print(f"Minimum usage threshold (10%): {min_usage} out of {len(records)}")
        
        # Sort by usage frequency
        for field_name, count in sorted(field_usage.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(records)) * 100
            included = "✓" if count >= min_usage else "✗"
            print(f"  {included} {field_name}: {count}/{len(records)} ({percentage:.1f}%)")
        
        # Check specific fields we're interested in
        target_fields = ['left_pco', 'right_pco', 'left_power_phase', 'right_power_phase']
        print(f"\nTarget field analysis:")
        for field_name in target_fields:
            count = field_usage.get(field_name, 0)
            percentage = (count / len(records)) * 100
            in_record_25 = field_name in records[25]
            print(f"  {field_name}: {count}/{len(records)} ({percentage:.1f}%) - In record[25]: {in_record_25}")

if __name__ == "__main__":
    debug_field_usage()