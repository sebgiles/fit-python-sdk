#!/usr/bin/env python3
"""Debug message data writing to find the left_pco bug"""

import os
import tempfile
from garmin_fit_sdk import Encoder

def debug_message_data_writing():
    print("=== DEBUGGING MESSAGE DATA WRITING ===")
    
    # Simple test case with PCO fields
    test_messages = {
        'file_id_mesgs': [{'type': 'activity', 'manufacturer': 'garmin', 'time_created': 1000000000}],
        'record_mesgs': [
            {'timestamp': 1000000001, 'left_pco': -5, 'right_pco': 3, 'heart_rate': 125}
        ]
    }
    
    # Patch the message data writing method
    original_write_message_data = Encoder._write_message_data
    
    def debug_write_message_data(self, local_msg_num, msg_profile, message):
        print(f"\n_write_message_data: local_msg_num={local_msg_num}")
        print(f"  Message: {message}")
        
        if 'left_pco' in message or 'right_pco' in message:
            print("  *** Processing message with PCO fields ***")
            
            # Get field definitions
            msg_def = self._local_mesg_defs[local_msg_num]
            field_defs = msg_def['field_defs']
            
            print(f"  Field definitions: {len(field_defs)}")
            for field_def in field_defs:
                field_id = field_def['field_id']
                
                # Find field name using our mapping
                field_name = None
                for name, fid in msg_def.get('field_name_to_id', {}).items():
                    if fid == field_id:
                        field_name = name
                        break
                
                print(f"    Field ID {field_id}: {field_name}")
                
                if field_name in ['left_pco', 'right_pco']:
                    print(f"      *** PCO FIELD: {field_name} ***")
                    
                    # Check if field exists in message
                    if field_name in message:
                        field_value = message[field_name]
                        print(f"        Value in message: {field_value}")
                        
                        # Check profile lookup
                        field_profile = msg_profile['fields'].get(field_id, {})
                        print(f"        Profile lookup by ID {field_id}: {bool(field_profile)}")
                        
                        # Correct profile lookup should be by field name or search
                        if not field_profile:
                            # Try by field name
                            if field_name in msg_profile['fields']:
                                field_profile = msg_profile['fields'][field_name]
                                print(f"        Profile lookup by name '{field_name}': FOUND")
                            else:
                                # Search by field ID
                                for fname, finfo in msg_profile['fields'].items():
                                    if finfo.get('num') == field_id:
                                        field_profile = finfo
                                        print(f"        Profile lookup by searching for ID {field_id}: FOUND as {fname}")
                                        break
                                else:
                                    print(f"        Profile lookup: NOT FOUND!")
                        
                    else:
                        print(f"        ❌ Field {field_name} NOT IN MESSAGE!")
        
        return original_write_message_data(self, local_msg_num, msg_profile, message)
    
    # Apply patch
    Encoder._write_message_data = debug_write_message_data
    
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
        Encoder._write_message_data = original_write_message_data

if __name__ == '__main__':
    debug_message_data_writing()