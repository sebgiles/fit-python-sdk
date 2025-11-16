#!/usr/bin/env python3
"""Debug PCO field encoding step by step"""

import os
import tempfile
from garmin_fit_sdk import Profile, Encoder

def debug_pco_encoding():
    print("=== DEBUGGING PCO FIELD ENCODING ===")
    
    # Simple test case with PCO fields
    test_messages = {
        'file_id_mesgs': [{'type': 'activity', 'manufacturer': 'garmin', 'time_created': 1000000000}],
        'record_mesgs': [
            {'timestamp': 1000000000, 'heart_rate': 120},
            {'timestamp': 1000000001, 'left_pco': -5, 'right_pco': 3, 'heart_rate': 125}
        ]
    }
    
    # Check message number lookup
    print("1. Message number lookup:")
    encoder = Encoder({})  # Empty encoder to test lookup
    
    for msg_type in test_messages.keys():
        global_num = encoder._get_global_message_number(msg_type)
        print(f"   {msg_type} -> global_num = {global_num}")
        
        if global_num is not None and global_num in Profile['messages']:
            msg_profile = Profile['messages'][global_num]
            print(f"   Profile found: {len(msg_profile.get('fields', {}))} fields")
            
            # Check for PCO fields specifically
            if global_num == 20:  # record
                for field_name in ['left_pco', 'right_pco']:
                    if field_name in msg_profile['fields']:
                        field_info = msg_profile['fields'][field_name]
                        print(f"   ✓ Found {field_name}: {field_info}")
                    else:
                        # Try by field ID
                        found_by_id = False
                        for field_id, field_info in msg_profile['fields'].items():
                            if field_info.get('name') == field_name:
                                print(f"   ✓ Found {field_name} by ID {field_id}: {field_info}")
                                found_by_id = True
                                break
                        if not found_by_id:
                            print(f"   ✗ {field_name} NOT FOUND!")
    
    # Test encoding with detailed tracing
    print(f"\n2. Encoding test:")
    
    # Temporarily patch the encoder to add debug output
    original_write_message_definition = Encoder._write_message_definition
    
    def debug_write_message_definition(self, local_msg_num, global_msg_num, msg_profile, pattern_messages):
        print(f"   Creating definition for msg {global_msg_num}, local {local_msg_num}")
        sample_message = pattern_messages[0]
        field_names = [name for name, value in sample_message.items() 
                      if not isinstance(name, int) and value is not None]
        print(f"   Field names in sample: {field_names}")
        
        # Check each field
        for field_name in field_names:
            if field_name in msg_profile['fields']:
                field_profile = msg_profile['fields'][field_name]
                print(f"   ✓ {field_name} found in profile: ID {field_profile['num']}")
            else:
                # Try to find field by name
                field_profile = None
                for field_id, fp in msg_profile['fields'].items():
                    if fp['name'] == field_name:
                        field_profile = fp
                        print(f"   ✓ {field_name} found by name search: ID {field_profile['num']}")
                        break
                
                if field_profile is None:
                    print(f"   ✗ {field_name} NOT FOUND - will be skipped!")
        
        return original_write_message_definition(self, local_msg_num, global_msg_num, msg_profile, pattern_messages)
    
    # Apply the patch
    Encoder._write_message_definition = debug_write_message_definition
    
    try:
        encoder = Encoder(test_messages)
        
        with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            success = encoder.write_to_file(temp_path)
            print(f"   Encoding result: {success}")
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    finally:
        # Restore original method
        Encoder._write_message_definition = original_write_message_definition

if __name__ == '__main__':
    debug_pco_encoding()