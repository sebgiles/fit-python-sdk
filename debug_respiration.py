#!/usr/bin/env python3

import sys
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.encoder import Encoder
from garmin_fit_sdk.profile import Profile

def debug_respiration_encoding():
    fit_file = "tests/fits/WithGearChangeData.fit"
    
    # Decode the file
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    stream.reset()
    messages, errors = decoder.read()
    
    # Find record message with enhanced_respiration_rate
    if 'record_mesgs' in messages:
        records = messages['record_mesgs']
        
        for i, record in enumerate(records):
            if 'enhanced_respiration_rate' in record:
                print(f"\n=== Record[{i}] ===")
                print(f"enhanced_respiration_rate: {record['enhanced_respiration_rate']}")
                
                # Check if respiration_rate field is also there
                if 'respiration_rate' in record:
                    print(f"respiration_rate: {record['respiration_rate']}")
                else:
                    print("respiration_rate: NOT FOUND")
                
                # Check profile to see if field 99 is in record message
                msg_profile = Profile['messages'][20]  # record message
                print(f"\nProfile check:")
                
                if 99 in msg_profile['fields']:
                    field_99 = msg_profile['fields'][99]
                    print(f"Field 99 found in record profile: {field_99['name']}")
                    print(f"Has components: {field_99['has_components']}")
                    print(f"Components: {field_99['components']}")
                else:
                    print("Field 99 NOT found in record profile")
                
                if 'enhanced_respiration_rate' in msg_profile['fields']:
                    print(f"enhanced_respiration_rate found directly in record profile")
                else:
                    # Check by field name
                    found_by_name = None
                    for fid, fprofile in msg_profile['fields'].items():
                        if fprofile['name'] == 'enhanced_respiration_rate':
                            found_by_name = fid
                            break
                    
                    if found_by_name:
                        print(f"enhanced_respiration_rate found by name search: field {found_by_name}")
                    else:
                        print("enhanced_respiration_rate NOT found in record profile by name")
                
                break
        else:
            print("No record with enhanced_respiration_rate found")

if __name__ == "__main__":
    debug_respiration_encoding()