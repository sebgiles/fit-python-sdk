#!/usr/bin/env python3
"""Test array field type determination"""

from garmin_fit_sdk import Encoder

def test_array_type_determination():
    # Simulate the problematic array
    problematic_array = [0, 24, 8, 7, 2, 3, 14, 13, 16, 1, 23, 26, 29, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
    
    encoder = Encoder({})
    
    print(f"Testing array: {problematic_array[:15]}...")
    
    try:
        elem_type, elem_size = encoder._determine_field_type_and_size({}, problematic_array[0])
        print(f"First element type: {elem_type}, size: {elem_size}")
        
        total_type, total_size = encoder._determine_field_type_and_size({}, problematic_array)
        print(f"Array type: {total_type}, total size: {total_size}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_array_type_determination()