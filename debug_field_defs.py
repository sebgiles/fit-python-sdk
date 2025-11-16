#!/usr/bin/env python3
"""Debug field definition creation"""

import os
import tempfile
from garmin_fit_sdk import Encoder

def debug_field_definitions():
    print("=== DEBUGGING FIELD DEFINITION CREATION ===")
    
    # Simple test case with PCO fields
    test_messages = {
        'file_id_mesgs': [{'type': 'activity', 'manufacturer': 'garmin', 'time_created': 1000000000}],
        'record_mesgs': [
            {'timestamp': 1000000000, 'heart_rate': 120},
            {'timestamp': 1000000001, 'left_pco': -5, 'right_pco': 3, 'heart_rate': 125}
        ]
    }
    
    # Patch the specific method to show field definitions
    original_write_specific_message_definition = Encoder._write_specific_message_definition
    
    def debug_write_specific_message_definition(self, local_msg_num, global_msg_num, msg_profile, message_fields, sample_message):
        print(f"\n_write_specific_message_definition: local={local_msg_num}, global={global_msg_num}")
        print(f"  Input message_fields: {sorted(message_fields)}")
        
        if 'left_pco' in message_fields or 'right_pco' in message_fields:
            print("  *** Processing PCO fields ***")
        
        # Call original to build field_defs, but capture the result
        result = original_write_specific_message_definition(self, local_msg_num, global_msg_num, msg_profile, message_fields, sample_message)
        
        # Check what field definitions were actually created
        if hasattr(self, '_local_mesg_defs') and local_msg_num in self._local_mesg_defs:
            msg_def = self._local_mesg_defs[local_msg_num]
            field_defs = msg_def['field_defs']
            
            print(f"  Created {len(field_defs)} field definitions:")
            for field_def in field_defs:
                print(f"    Field ID {field_def['field_id']}: size={field_def['size']}, base_type={field_def['base_type']}")
                
                # Look up field name from profile
                for field_id, field_info in msg_profile['fields'].items():
                    if field_info['num'] == field_def['field_id']:
                        field_name = field_info['name']
                        print(f"      -> {field_name}")
                        if field_name in ['left_pco', 'right_pco']:
                            print(f"      *** PCO FIELD INCLUDED! ***")
                        break
            
            # Check if PCO fields are missing
            has_left_pco = any(fd['field_id'] == 67 for fd in field_defs)
            has_right_pco = any(fd['field_id'] == 68 for fd in field_defs)
            
            if ('left_pco' in message_fields) != has_left_pco:
                print(f"  ❌ left_pco mismatch: in_input={('left_pco' in message_fields)}, in_defs={has_left_pco}")
            if ('right_pco' in message_fields) != has_right_pco:
                print(f"  ❌ right_pco mismatch: in_input={('right_pco' in message_fields)}, in_defs={has_right_pco}")
        
        return result
    
    # Apply patch
    Encoder._write_specific_message_definition = debug_write_specific_message_definition
    
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
        Encoder._write_specific_message_definition = original_write_specific_message_definition

if __name__ == '__main__':
    debug_field_definitions()