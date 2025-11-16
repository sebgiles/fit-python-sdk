#!/usr/bin/env python3
"""Check for None values in HrmPluginTestActivity.fit"""

from garmin_fit_sdk import Decoder, Stream

def analyze_none_values():
    print("=== ANALYZING NONE VALUES ===")
    
    original_file = "tests/fits/HrmPluginTestActivity.fit"
    
    # Decode original file
    original_stream = Stream.from_file(original_file)
    original_decoder = Decoder(original_stream)
    original_messages, original_errors = original_decoder.read()
    
    print(f"Decoded {len(original_messages)} message types")
    
    # Check for None values in each message type
    total_none_count = 0
    
    for msg_type, messages in original_messages.items():
        none_count_this_type = 0
        field_none_counts = {}
        
        for i, message in enumerate(messages):
            for field_name, field_value in message.items():
                if field_value is None:
                    none_count_this_type += 1
                    total_none_count += 1
                    
                    if field_name not in field_none_counts:
                        field_none_counts[field_name] = 0
                    field_none_counts[field_name] += 1
        
        if none_count_this_type > 0:
            print(f"\n{msg_type}: {len(messages)} messages, {none_count_this_type} None values")
            for field_name, count in sorted(field_none_counts.items()):
                print(f"  {field_name}: {count} None values")
    
    print(f"\nTotal None values across all messages: {total_none_count}")
    
    # Now check if we can find any fields that specifically might cause int() issues
    print(f"\n=== CHECKING SPECIFIC PROBLEMATIC PATTERNS ===")
    
    for msg_type, messages in original_messages.items():
        for i, message in enumerate(messages):
            for field_name, field_value in message.items():
                # Look for any field that might be processed as int but contains None
                if field_value is None:
                    # Check if this field name suggests it should be numeric
                    if any(word in field_name.lower() for word in ['time', 'id', 'num', 'count', 'index', 'type']):
                        print(f"Potential issue: {msg_type}[{i}].{field_name} is None (sounds numeric)")

if __name__ == '__main__':
    analyze_none_values()