#!/usr/bin/env python3

import sys
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.encoder import Encoder
from garmin_fit_sdk.profile import Profile

def debug_missing_fields():
    fit_file = "tests/fits/WithGearChangeData.fit"
    
    # Decode the file
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    stream.reset()
    messages, errors = decoder.read()
    
    # Check record message 25
    if 'record_mesgs' in messages:
        records = messages['record_mesgs']
        
        if len(records) > 25:
            record = records[25]
            print(f"\n=== Record[25] ===")
            
            missing_fields = ['right_pco', 'left_pco', 'fractional_cadence', 'cadence']
            msg_profile = Profile['messages'][20]  # record message
            
            for field_name in missing_fields:
                print(f"\n--- Field: {field_name} ---")
                
                # Check if field exists in original message
                if field_name in record:
                    print(f"Value in original: {record[field_name]}")
                else:
                    print("NOT in original message")
                    continue
                
                # Check if field exists in profile
                if field_name in msg_profile['fields']:
                    field_profile = msg_profile['fields'][field_name]
                    print(f"Found directly in profile: {field_profile['num']}")
                else:
                    # Check by name search
                    found_by_name = None
                    for fid, fprofile in msg_profile['fields'].items():
                        if fprofile['name'] == field_name:
                            found_by_name = (fid, fprofile)
                            break
                    
                    if found_by_name:
                        fid, fprofile = found_by_name
                        print(f"Found by name search: field {fid}")
                        print(f"Type: {fprofile['type']}")
                        print(f"Scale: {fprofile.get('scale', 'N/A')}")
                        print(f"Offset: {fprofile.get('offset', 'N/A')}")
                    else:
                        print("NOT found in profile at all")
            
            # Now let's encode this record and see what gets skipped
            print(f"\n=== Encoder Debug ===")
            encoder = Encoder(messages)
            
            # Check field definitions for record message
            print(f"Encoder would process these fields from record[25]:")
            for field_name, field_value in record.items():
                if isinstance(field_name, int):
                    print(f"  {field_name} (numeric): {field_value} -> SKIP (numeric field)")
                    continue
                
                if field_name in msg_profile['fields']:
                    field_profile = msg_profile['fields'][field_name]
                    print(f"  {field_name}: {field_value} -> field {field_profile['num']} (direct)")
                else:
                    # Try to find field by name
                    field_profile = None
                    for field_id, fp in msg_profile['fields'].items():
                        if fp['name'] == field_name:
                            field_profile = fp
                            break
                    
                    if field_profile:
                        print(f"  {field_name}: {field_value} -> field {field_profile['num']} (by name)")
                    else:
                        print(f"  {field_name}: {field_value} -> SKIP (not in profile)")

if __name__ == "__main__":
    debug_missing_fields()