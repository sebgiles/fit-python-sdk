#!/usr/bin/env python3

import sys
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.profile import Profile

def analyze_decoder_information():
    """Analyze what information is available vs missing from decoder output"""
    fit_file = "tests/fits/WithGearChangeData.fit"
    
    # Decode with different options to see what info is preserved
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    stream.reset()
    
    print("=== DECODER OUTPUT ANALYSIS ===\n")
    
    # Standard decoding
    messages, errors = decoder.read()
    
    # Check a sample record message
    if 'record_mesgs' in messages:
        record = messages['record_mesgs'][25]  # Our problematic record
        
        print(f"1. FIELD INFORMATION AVAILABLE:")
        print(f"   - Field names: {list(record.keys())}")
        print(f"   - Sample field values: timestamp={record.get('timestamp')}, power={record.get('power')}")
        
        # Check if we have raw field information
        print(f"\n2. MISSING INFORMATION:")
        
        # Do we know field IDs?
        print(f"   - Field IDs: NOT directly available (only field names)")
        
        # Do we know base types?
        print(f"   - Field base types: NOT directly available (must infer from profile)")
        
        # Do we know field order in original message?
        print(f"   - Original field order: NOT available (Python dict has insertion order but may not match FIT order)")
        
        # Do we know message definition details?
        print(f"   - Message definition details: NOT available")
        
        # Do we have component vs base field distinction?
        print(f"   - Component field markers: NOT available (enhanced_respiration_rate looks like regular field)")
        
        print(f"\n3. WHAT WE NEED TO RECONSTRUCT:")
        
        # Field definitions
        msg_profile = Profile['messages'][20]  # record message
        
        fields_in_record = []
        unknown_fields = []
        
        for field_name in record.keys():
            if isinstance(field_name, int):
                unknown_fields.append(field_name)
                continue
                
            # Try to find in profile
            found = False
            for field_id, field_profile in msg_profile['fields'].items():
                if field_profile['name'] == field_name:
                    fields_in_record.append({
                        'name': field_name,
                        'id': field_id,
                        'type': field_profile['type'],
                        'value': record[field_name]
                    })
                    found = True
                    break
            
            if not found:
                print(f"   - MISSING FROM PROFILE: {field_name}")
        
        print(f"   - Identified fields: {len(fields_in_record)}")
        print(f"   - Unknown numeric fields: {unknown_fields}")
        
        # Check for component fields
        component_fields = []
        base_fields = []
        
        for field_info in fields_in_record:
            field_id = field_info['id']
            field_name = field_info['name']
            
            # Is this field a component of another field?
            is_component = False
            for parent_id, parent_profile in msg_profile['fields'].items():
                if (parent_profile.get('has_components', False) and 
                    'components' in parent_profile and 
                    field_id in parent_profile['components']):
                    component_fields.append({
                        'component': field_name,
                        'parent': parent_profile['name'],
                        'parent_id': parent_id
                    })
                    is_component = True
                    break
            
            if not is_component:
                base_fields.append(field_name)
        
        print(f"\n4. COMPONENT ANALYSIS:")
        print(f"   - Base fields: {base_fields}")
        print(f"   - Component fields: {component_fields}")
        
        print(f"\n5. CRITICAL MISSING INFO:")
        print(f"   - Which fields were actually in the ORIGINAL message definition")
        print(f"   - Which fields are decoder-expanded components")
        print(f"   - Original field order and sizes")
        print(f"   - Whether message used multiple local message numbers")

if __name__ == "__main__":
    analyze_decoder_information()