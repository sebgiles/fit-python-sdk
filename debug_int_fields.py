#!/usr/bin/env python3
"""Debug integer field keys specifically"""

from garmin_fit_sdk import Decoder, Stream

def debug_int_fields():
    print("=== ANALYZING INTEGER FIELD KEYS ===")
    
    original_file = "tests/fits/HrmPluginTestActivity.fit"
    
    # Decode original file
    original_stream = Stream.from_file(original_file)
    original_decoder = Decoder(original_stream)
    original_messages, _ = original_decoder.read()
    
    # Analyze integer field keys
    int_field_stats = {}
    total_int_fields = 0
    
    for msg_type, messages in original_messages.items():
        int_fields_this_type = 0
        int_field_values = {}
        
        for message in messages:
            for field_name, field_value in message.items():
                if isinstance(field_name, int):
                    total_int_fields += 1
                    int_fields_this_type += 1
                    
                    if field_name not in int_field_values:
                        int_field_values[field_name] = []
                    int_field_values[field_name].append(field_value)
        
        if int_fields_this_type > 0:
            int_field_stats[msg_type] = {
                'count': int_fields_this_type,
                'fields': int_field_values
            }
    
    print(f"Total messages with integer field keys: {len(int_field_stats)}")
    print(f"Total integer field instances: {total_int_fields}")
    
    for msg_type, stats in int_field_stats.items():
        print(f"\n{msg_type}: {stats['count']} integer fields")
        for field_id, values in stats['fields'].items():
            # Handle lists and other non-hashable types
            try:
                unique_values = set(values)
                unique_count = len(unique_values)
                sample_values = list(unique_values)[:5]
            except TypeError:
                # Handle lists and other non-hashable types
                unique_count = "unknown (has lists/arrays)"
                sample_values = values[:5]
            
            print(f"  Field {field_id}: {len(values)} instances, {unique_count} unique values")
            
            # Check for None values specifically
            none_count = sum(1 for v in values if v is None)
            if none_count > 0:
                print(f"    ⚠️ {none_count} None values!")
            
            # Check for list/array values  
            list_count = sum(1 for v in values if isinstance(v, list))
            if list_count > 0:
                print(f"    📋 {list_count} list/array values!")
            
            # Show sample values
            if len(sample_values) > 0:
                print(f"    Sample values: {sample_values}")

if __name__ == '__main__':
    debug_int_fields()