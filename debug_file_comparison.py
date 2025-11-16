#!/usr/bin/env python3
"""Compare the three test files to find what makes HrmPluginTestActivity.fit different"""

from garmin_fit_sdk import Decoder, Stream

def compare_test_files():
    files = [
        ("ActivityDevFields.fit", "tests/fits/ActivityDevFields.fit"),
        ("HrmPluginTestActivity.fit", "tests/fits/HrmPluginTestActivity.fit"), 
        ("WithGearChangeData.fit", "tests/fits/WithGearChangeData.fit")
    ]
    
    print("=== COMPARING TEST FILES ===")
    
    for name, filepath in files:
        print(f"\n{name}:")
        
        # Decode
        stream = Stream.from_file(filepath)
        decoder = Decoder(stream)
        messages, errors = decoder.read()
        
        print(f"  Message types: {len(messages)}")
        print(f"  Total messages: {sum(len(msgs) for msgs in messages.values())}")
        
        # Count integer fields
        int_fields = 0
        none_values = 0
        array_fields = 0
        
        for msg_type, msg_list in messages.items():
            for msg in msg_list:
                for field_name, field_value in msg.items():
                    if isinstance(field_name, int):
                        int_fields += 1
                        
                    if field_value is None:
                        none_values += 1
                        
                    if isinstance(field_value, list):
                        array_fields += 1
                        # Check for None in arrays
                        if any(v is None for v in field_value):
                            none_values += field_value.count(None)
        
        print(f"  Integer field keys: {int_fields}")
        print(f"  None values: {none_values}")
        print(f"  Array fields: {array_fields}")
        
        # Check message types unique to each file
        unique_types = set(messages.keys())
        print(f"  Message types: {sorted(unique_types)}")

if __name__ == '__main__':
    compare_test_files()