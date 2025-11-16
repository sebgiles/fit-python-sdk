#!/usr/bin/env python3
"""Debug encoder execution flow"""

import os
import tempfile
from garmin_fit_sdk import Encoder

def debug_encoder_flow():
    print("=== DEBUGGING ENCODER FLOW ===")
    
    # Simple test case with PCO fields
    test_messages = {
        'file_id_mesgs': [{'type': 'activity', 'manufacturer': 'garmin', 'time_created': 1000000000}],
        'record_mesgs': [
            {'timestamp': 1000000000, 'heart_rate': 120},
            {'timestamp': 1000000001, 'left_pco': -5, 'right_pco': 3, 'heart_rate': 125}
        ]
    }
    
    # Patch multiple methods to trace execution
    original_write_messages = Encoder._write_messages
    original_write_message_type = Encoder._write_message_type
    original_write_message_definition = Encoder._write_message_definition
    
    def debug_write_messages(self):
        print("   _write_messages called")
        for msg_type, messages in self._messages.items():
            print(f"   Processing {msg_type}: {len(messages)} messages")
            if msg_type == 'record_mesgs':
                for i, msg in enumerate(messages):
                    fields = [f for f in msg.keys() if not isinstance(f, int)]
                    print(f"     Message {i}: {fields}")
                    if 'left_pco' in msg or 'right_pco' in msg:
                        print(f"       *** HAS PCO FIELDS: left_pco={msg.get('left_pco')}, right_pco={msg.get('right_pco')}")
        return original_write_messages(self)
    
    def debug_write_message_type(self, message_type_num, messages):
        print(f"   _write_message_type called: msg_type={message_type_num}, {len(messages)} messages")
        return original_write_message_type(self, message_type_num, messages)
    
    def debug_write_message_definition(self, local_msg_num, global_msg_num, msg_profile, pattern_messages):
        print(f"   _write_message_definition: local={local_msg_num}, global={global_msg_num}")
        sample_message = pattern_messages[0] 
        field_names = [name for name, value in sample_message.items() 
                      if not isinstance(name, int) and value is not None]
        print(f"     Sample message fields: {field_names}")
        
        if 'left_pco' in field_names or 'right_pco' in field_names:
            print("     *** SAMPLE HAS PCO FIELDS ***")
            
            # Check profile lookup for PCO fields
            for field_name in ['left_pco', 'right_pco']:
                if field_name in field_names:
                    if field_name in msg_profile['fields']:
                        print(f"     ✓ {field_name} found in profile")
                    else:
                        # Try by name search
                        found = False
                        for field_id, fp in msg_profile['fields'].items():
                            if fp['name'] == field_name:
                                print(f"     ✓ {field_name} found by name search")
                                found = True
                                break
                        if not found:
                            print(f"     ✗ {field_name} NOT FOUND in profile!")
        
        return original_write_message_definition(self, local_msg_num, global_msg_num, msg_profile, pattern_messages)
    
    # Apply patches
    Encoder._write_messages = debug_write_messages
    Encoder._write_message_type = debug_write_message_type  
    Encoder._write_message_definition = debug_write_message_definition
    
    try:
        encoder = Encoder(test_messages)
        
        with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            print("Starting encoding...")
            success = encoder.write_to_file(temp_path)
            print(f"Encoding result: {success}")
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    finally:
        # Restore original methods
        Encoder._write_messages = original_write_messages
        Encoder._write_message_type = original_write_message_type
        Encoder._write_message_definition = original_write_message_definition

if __name__ == '__main__':
    debug_encoder_flow()