#!/usr/bin/env python3
"""Debug specific message definition creation"""

import os
import tempfile
from garmin_fit_sdk import Encoder

def debug_specific_definition():
    print("=== DEBUGGING SPECIFIC MESSAGE DEFINITION ===")
    
    # Simple test case with PCO fields
    test_messages = {
        'file_id_mesgs': [{'type': 'activity', 'manufacturer': 'garmin', 'time_created': 1000000000}],
        'record_mesgs': [
            {'timestamp': 1000000000, 'heart_rate': 120},
            {'timestamp': 1000000001, 'left_pco': -5, 'right_pco': 3, 'heart_rate': 125}
        ]
    }
    
    # Patch the specific method
    original_write_specific_message_definition = Encoder._write_specific_message_definition
    
    def debug_write_specific_message_definition(self, local_msg_num, global_msg_num, msg_profile, message_fields, sample_message):
        print(f"\n   _write_specific_message_definition: local={local_msg_num}, global={global_msg_num}")
        print(f"     Message fields: {message_fields}")
        print(f"     Sample message: {sample_message}")
        
        if 'left_pco' in message_fields or 'right_pco' in message_fields:
            print("     *** HAS PCO FIELDS ***")
            
            # Check profile lookup for PCO fields
            for field_name in ['left_pco', 'right_pco']:
                if field_name in message_fields:
                    print(f"     Checking {field_name}...")
                    
                    if field_name in msg_profile['fields']:
                        field_profile = msg_profile['fields'][field_name]
                        print(f"       ✓ Found directly: {field_profile}")
                    else:
                        # Try by name search (this is what the encoder actually does)
                        field_profile = None
                        for field_id, fp in msg_profile['fields'].items():
                            if fp['name'] == field_name:
                                field_profile = fp
                                print(f"       ✓ Found by name search: {field_profile}")
                                break
                        
                        if field_profile is None:
                            print(f"       ✗ NOT FOUND - field will be SKIPPED!")
                            print(f"       Available fields: {list(msg_profile['fields'].keys())}")
                            
                            # Show first few fields for debugging
                            print("       First few field names in profile:")
                            count = 0
                            for field_id, fp in msg_profile['fields'].items():
                                if count < 10:
                                    print(f"         {field_id}: {fp.get('name', 'NO_NAME')}")
                                    count += 1
        
        return original_write_specific_message_definition(self, local_msg_num, global_msg_num, msg_profile, message_fields, sample_message)
    
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
    debug_specific_definition()