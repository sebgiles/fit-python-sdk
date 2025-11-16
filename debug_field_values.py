#!/usr/bin/env python3
"""Debug exact field value writing"""

import os
import tempfile
from garmin_fit_sdk import Encoder

def debug_field_value_writing():
    print("=== DEBUGGING FIELD VALUE WRITING ===")
    
    # Simple test case with PCO fields
    test_messages = {
        'file_id_mesgs': [{'type': 'activity', 'manufacturer': 'garmin', 'time_created': 1000000000}],
        'record_mesgs': [
            {'timestamp': 1000000001, 'left_pco': -5, 'right_pco': 3, 'heart_rate': 125}
        ]
    }
    
    # Patch the field value writing method
    original_write_single_value = Encoder._write_single_value
    
    def debug_write_single_value(self, value, base_type, field_profile):
        # Only debug PCO fields
        if field_profile and field_profile.get('name') in ['left_pco', 'right_pco']:
            field_name = field_profile['name']
            print(f"    _write_single_value: {field_name} = {value}")
            print(f"      base_type: {base_type}")
            print(f"      field_profile: {field_profile}")
            
            # Check scaling
            if 'scale' in field_profile and 'offset' in field_profile:
                scale = field_profile['scale'][0] if field_profile['scale'] else 1
                offset = field_profile['offset'][0] if field_profile['offset'] else 0
                print(f"      scale: {scale}, offset: {offset}")
                
                if scale != 1 or offset != 0:
                    scaled_value = (value + offset) * scale
                    print(f"      scaled value: {scaled_value}")
            
            # Show what bytes will be written
            from garmin_fit_sdk.fit import FIT
            import struct
            
            base_type_def = FIT.BASE_TYPE_DEFINITIONS[base_type]
            type_code = base_type_def['type_code']
            
            try:
                if type_code in ['b', 'B']:
                    packed = struct.pack('<' + type_code, int(value) & 0xFF)
                elif type_code in ['h', 'H']:
                    packed = struct.pack('<' + type_code, int(value) & 0xFFFF)
                else:
                    packed = struct.pack('<' + type_code, int(value))
                    
                print(f"      bytes to write: {packed.hex()}")
            except Exception as e:
                print(f"      packing error: {e}")
        
        return original_write_single_value(self, value, base_type, field_profile)
    
    # Apply patch
    Encoder._write_single_value = debug_write_single_value
    
    try:
        encoder = Encoder(test_messages)
        
        with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            print("Starting encoding...")
            success = encoder.write_to_file(temp_path)
            print(f"\nEncoding result: {success}")
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    finally:
        # Restore original method
        Encoder._write_single_value = original_write_single_value

if __name__ == '__main__':
    debug_field_value_writing()