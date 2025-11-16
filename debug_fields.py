#!/usr/bin/env python3

import sys
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder

def debug_enhanced_respiration_rate():
    fit_file = "tests/fits/WithGearChangeData.fit"
    
    # Decode the file
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    stream.reset()
    messages, errors = decoder.read()
    
    print(f"Decoding errors: {errors}")
    print(f"Total message types: {len(messages)}")
    
    # Check for record messages that have enhanced_respiration_rate
    if 'record_mesgs' in messages:
        records = messages['record_mesgs']
        print(f"Found {len(records)} record messages")
        
        # Check each record for enhanced_respiration_rate
        for i, record in enumerate(records):
            if 'enhanced_respiration_rate' in record:
                print(f"Record[{i}] has enhanced_respiration_rate: {record['enhanced_respiration_rate']}")
                print(f"All fields in record[{i}]: {list(record.keys())}")
                break
        else:
            print("No record has enhanced_respiration_rate field")
            # Show all fields in first few records
            for i in range(min(3, len(records))):
                print(f"Record[{i}] fields: {list(records[i].keys())}")

if __name__ == "__main__":
    debug_enhanced_respiration_rate()