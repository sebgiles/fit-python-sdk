#!/usr/bin/env python3

from garmin_fit_sdk import Decoder, Stream, Profile

def main():
    print("=== Checking PCO field definitions ===")
    
    # Access the Profile data directly
    from garmin_fit_sdk.profile import Profile as ProfileData
    messages = ProfileData['messages']
    record_def = messages[20]  # Record message is #20
    record_fields = record_def['fields']
    
    print(f"Record message has {len(record_fields)} field definitions")
    
    # Look for PCO fields specifically
    for field_num in [67, 68]:
        if field_num in record_fields:
            field_def = record_fields[field_num]
            print(f"Field {field_num}: {field_def['name']} - {field_def['type']}")
        else:
            print(f"Field {field_num}: NOT FOUND")
    
    # Test actual decoding with original FIT file
    print("\n=== Testing original file decode ===")
    decoder = Decoder('/home/seb/personal/strava/fit-python-sdk/tests/fits/WithGearChangeData.fit')
    messages, errors = decoder.read(
        expand_components=False,
        expand_sub_fields=False,
        merge_heart_rates=False
    )
    
    print(f"Decode errors: {errors}")
    
    if 'record_mesgs' in messages:
        records = messages['record_mesgs']
        
        # Find a record with PCO fields
        pco_record = None
        for i, record in enumerate(records):
            if 'left_pco' in record and 'right_pco' in record:
                pco_record = record
                print(f"\nFound PCO fields in record {i}:")
                print(f"  left_pco: {record['left_pco']}")
                print(f"  right_pco: {record['right_pco']}")
                print(f"  All fields: {sorted(record.keys())}")
                break
        
        if pco_record is None:
            print("\nNo records with both PCO fields found!")
            # Check first few records
            for i, record in enumerate(records[:5]):
                fields = sorted(record.keys())
                has_left = 'left_pco' in record
                has_right = 'right_pco' in record
                numeric_fields = [k for k in record.keys() if isinstance(k, int)]
                print(f"Record {i}: left_pco={has_left}, right_pco={has_right}, numeric_fields={numeric_fields}")

if __name__ == "__main__":
    main()