#!/usr/bin/env python3

import sys
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.profile import Profile

def debug_field_conflicts():
    fit_file = "tests/fits/WithGearChangeData.fit"
    
    # Decode the file
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    stream.reset()
    messages, errors = decoder.read()
    
    # Check record message profile for field ID conflicts
    msg_profile = Profile['messages'][20]  # record message
    
    # Get record[25]
    record = messages['record_mesgs'][25]
    
    # Check the field IDs for our problematic fields
    problematic_fields = {
        'left_pco': None,
        'right_pco': None,
        'left_power_phase': None,
        'right_power_phase': None,
        'left_power_phase_peak': None,
        'right_power_phase_peak': None
    }
    
    print(f"Field ID analysis:")
    for field_name in problematic_fields:
        # Find field profile
        field_profile = None
        for field_id, fp in msg_profile['fields'].items():
            if fp['name'] == field_name:
                field_profile = fp
                break
        
        if field_profile:
            field_id = field_profile['num']
            in_record_25 = field_name in record
            value = record.get(field_name, 'NOT_PRESENT')
            print(f"  {field_name}: field ID {field_id}, in record[25]: {in_record_25}, value: {value}")
            print(f"    Type: {field_profile['type']}, Scale: {field_profile.get('scale', [1])}, Offset: {field_profile.get('offset', [0])}")
        else:
            print(f"  {field_name}: NOT FOUND in profile")
    
    # Check for any field ID conflicts
    field_ids = {}
    for field_name in problematic_fields:
        for field_id, fp in msg_profile['fields'].items():
            if fp['name'] == field_name:
                if field_id in field_ids:
                    print(f"CONFLICT: Field ID {field_id} used by both {field_ids[field_id]} and {field_name}")
                else:
                    field_ids[field_id] = field_name

if __name__ == "__main__":
    debug_field_conflicts()