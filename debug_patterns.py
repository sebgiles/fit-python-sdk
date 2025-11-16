#!/usr/bin/env python3

import sys
import tempfile
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.encoder import Encoder

def debug_message_definitions():
    """Debug the message definition creation process"""
    fit_file = "tests/fits/WithGearChangeData.fit"
    
    # Get raw messages
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    stream.reset()
    
    raw_messages, _ = decoder.read(
        expand_components=False,
        expand_sub_fields=False,
        merge_heart_rates=False
    )
    
    print("=== MESSAGE DEFINITION DEBUG ===\n")
    
    if 'record_mesgs' in raw_messages:
        records = raw_messages['record_mesgs']
        
        # Test our pattern grouping logic
        encoder = Encoder(raw_messages)
        
        # Get field patterns for first 30 records to see grouping
        patterns = {}
        for i, record in enumerate(records[:30]):
            pattern = encoder._get_message_field_pattern(record)
            if pattern not in patterns:
                patterns[pattern] = []
            patterns[pattern].append(i)
        
        print(f"PATTERN GROUPS (first 30 records):")
        for i, (pattern, record_indices) in enumerate(patterns.items()):
            print(f"  Group {i+1}: {len(record_indices)} records")
            print(f"    Records: {record_indices}")
            print(f"    Fields: {sorted(pattern)}")
        
        # Check specific records
        record_0_pattern = encoder._get_message_field_pattern(records[0])
        record_25_pattern = encoder._get_message_field_pattern(records[25])
        
        print(f"\nSPECIFIC PATTERNS:")
        print(f"  Record[0] pattern: {sorted(record_0_pattern)}")
        print(f"  Record[25] pattern: {sorted(record_25_pattern)}")
        print(f"  Same pattern? {record_0_pattern == record_25_pattern}")
        
        # Test pattern-based grouping
        grouped = encoder._group_messages_by_field_pattern(records[:30])
        
        print(f"\nGROUPED RESULTS:")
        for i, (pattern, messages) in enumerate(grouped.items()):
            print(f"  Group {i+1}: {len(messages)} messages")
            print(f"    Pattern: {sorted(pattern)}")
            if record_25_pattern in grouped:
                record_25_group_size = len(grouped[record_25_pattern])
                print(f"    Record[25] is in a group of {record_25_group_size} messages")

if __name__ == "__main__":
    debug_message_definitions()