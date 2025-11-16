#!/usr/bin/env python3
"""Test with positive PCO values"""

import os
import tempfile
from garmin_fit_sdk import Decoder, Stream, Encoder

def test_positive_pco_values():
    print("=== TESTING POSITIVE PCO VALUES ===")
    
    # Test with both positive values
    test_messages = {
        'file_id_mesgs': [{'type': 'activity', 'manufacturer': 'garmin', 'time_created': 1000000000}],
        'record_mesgs': [
            {'timestamp': 1000000000, 'heart_rate': 120},
            {'timestamp': 1000000001, 'left_pco': 5, 'right_pco': 3, 'heart_rate': 125}
        ]
    }
    
    encoder = Encoder(test_messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        # Encode
        success = encoder.write_to_file(temp_path)
        print(f"Encoding: {success}")
        
        if success:
            # Decode
            stream = Stream.from_file(temp_path)
            decoder = Decoder(stream)
            messages, errors = decoder.read(
                expand_components=False,
                expand_sub_fields=False,
                merge_heart_rates=False
            )
            
            print(f"Decode errors: {errors}")
            
            if 'record_mesgs' in messages:
                records = messages['record_mesgs']
                print(f"Records: {len(records)}")
                
                for i, record in enumerate(records):
                    fields = sorted(record.keys())
                    has_pco = 'left_pco' in record and 'right_pco' in record
                    print(f"  Record {i}: {len(fields)} fields, PCO={has_pco}")
                    print(f"    Fields: {fields}")
                    
                    if has_pco:
                        print(f"    ✅ PCO: left={record['left_pco']}, right={record['right_pco']}")
                    else:
                        if 'left_pco' in record:
                            print(f"    Partial: left_pco={record['left_pco']}")
                        if 'right_pco' in record:
                            print(f"    Partial: right_pco={record['right_pco']}")
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    test_positive_pco_values()