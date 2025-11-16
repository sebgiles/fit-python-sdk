#!/usr/bin/env python3
"""Check profile structure"""

from garmin_fit_sdk import Profile

def check_profile_structure():
    print("=== PROFILE STRUCTURE ===")
    
    if 'messages' in Profile:
        print(f"Available message types: {len(Profile['messages'])}")
        for msg_type in sorted(Profile['messages'].keys()):
            print(f"  {msg_type}")
            
        # Check if there's a message type 20 (which should be record)
        record_msg_id = 20  # Record message is typically message ID 20
        if record_msg_id in Profile['messages']:
            print(f"\nFound record message (ID {record_msg_id}):")
            record_msg = Profile['messages'][record_msg_id]
            print(f"  Fields: {len(record_msg.get('fields', {}))}")
            
            # Look for PCO fields specifically
            if 'fields' in record_msg:
                for field_id, field_info in record_msg['fields'].items():
                    field_name = field_info.get('name', '')
                    if 'pco' in field_name.lower():
                        print(f"  FOUND PCO: {field_id}: {field_name} - {field_info}")
        else:
            print(f"\nRecord message (ID {record_msg_id}) not found!")
            
        # Let's check for any message that might have PCO fields
        print(f"\nLooking for PCO fields in any message type:")
        pco_fields_found = {}
        
        for msg_type, msg_info in Profile['messages'].items():
            if 'fields' in msg_info:
                for field_id, field_info in msg_info['fields'].items():
                    field_name = field_info.get('name', '')
                    if 'pco' in field_name.lower():
                        if msg_type not in pco_fields_found:
                            pco_fields_found[msg_type] = []
                        pco_fields_found[msg_type].append((field_id, field_name, field_info))
        
        if pco_fields_found:
            print(f"Found PCO fields:")
            for msg_type, fields in pco_fields_found.items():
                print(f"  {msg_type}:")
                for field_id, field_name, field_info in fields:
                    print(f"    {field_id}: {field_name} - {field_info}")
        else:
            print("No PCO fields found in any message type!")
    
    else:
        print("No messages found in Profile!")
        print(f"Profile keys: {Profile.keys()}")

if __name__ == '__main__':
    check_profile_structure()