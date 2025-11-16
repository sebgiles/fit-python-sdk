#!/usr/bin/env python3
"""Check if PCO fields exist in profile"""

from garmin_fit_sdk import Profile

def check_pco_fields():
    print("=== CHECKING PCO FIELDS IN PROFILE ===")
    
    # Look for PCO fields in record message type
    if 'record' in Profile['messages']:
        record_profile = Profile['messages']['record']
        
        print(f"Record message has {len(record_profile['fields'])} fields")
        
        # Check for PCO fields
        pco_fields = ['left_pco', 'right_pco']
        
        for pco_field in pco_fields:
            found = False
            
            # Check by field name
            for field_id, field_info in record_profile['fields'].items():
                if field_info['name'] == pco_field:
                    print(f"Found {pco_field}: field_id={field_id}, info={field_info}")
                    found = True
                    break
            
            if not found:
                print(f"Field {pco_field} NOT FOUND in record profile!")
        
        # Also show all fields for reference
        print(f"\nAll record fields:")
        for field_id, field_info in sorted(record_profile['fields'].items()):
            name = field_info['name'] 
            if 'pco' in name.lower():
                print(f"  {field_id}: {name} (*** PCO FIELD ***)")
            else:
                print(f"  {field_id}: {name}")
    else:
        print("Record message not found in profile!")

if __name__ == '__main__':
    check_pco_fields()