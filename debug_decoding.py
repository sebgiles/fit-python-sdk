#!/usr/bin/env python3
"""Debug what happens during decoding of our encoded file"""

import os
import tempfile
from garmin_fit_sdk import Decoder, Stream, Encoder

def debug_decoding_process():
    print("=== DEBUGGING DECODING PROCESS ===")
    
    # Simple test case with PCO fields
    test_messages = {
        'file_id_mesgs': [{'type': 'activity', 'manufacturer': 'garmin', 'time_created': 1000000000}],
        'record_mesgs': [
            {'timestamp': 1000000000, 'heart_rate': 120},
            {'timestamp': 1000000001, 'left_pco': -5, 'right_pco': 3, 'heart_rate': 125}
        ]
    }
    
    encoder = Encoder(test_messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        # Encode
        print("1. Encoding...")
        success = encoder.write_to_file(temp_path)
        print(f"   Success: {success}")
        
        file_size = os.path.getsize(temp_path)
        print(f"   File size: {file_size} bytes")
        
        # Show binary structure
        with open(temp_path, 'rb') as f:
            data = f.read()
            print(f"   Header: {data[:14].hex()}")
            print(f"   First 50 data bytes: {data[14:64].hex()}")
        
        # Try decoding step by step
        print(f"\n2. Decoding...")
        
        try:
            stream = Stream.from_file(temp_path)
            decoder = Decoder(stream)
            
            # Check basic validity
            stream.reset()
            print(f"   Is FIT: {decoder.is_fit()}")
            
            stream.reset()
            print(f"   Integrity OK: {decoder.check_integrity()}")
            
            # Try decode with minimal options
            stream.reset()
            messages, errors = decoder.read(
                expand_components=False,
                expand_sub_fields=False,
                merge_heart_rates=False
            )
            
            print(f"   Decode errors: {errors}")
            
            if not errors:
                print(f"   ✅ Decoding successful!")
                print(f"   Message types: {list(messages.keys())}")
                
                if 'record_mesgs' in messages:
                    records = messages['record_mesgs']
                    print(f"   Records: {len(records)}")
                    
                    for i, record in enumerate(records):
                        fields = sorted(record.keys())
                        has_pco = 'left_pco' in record and 'right_pco' in record
                        print(f"     Record {i}: {len(fields)} fields, PCO={has_pco}")
                        print(f"       Fields: {fields}")
                        
                        if has_pco:
                            print(f"       ✅ PCO values: left={record['left_pco']}, right={record['right_pco']}")
                        elif 'left_pco' in test_messages['record_mesgs'][i] or 'right_pco' in test_messages['record_mesgs'][i]:
                            print(f"       ❌ PCO fields missing! Should have been: left={test_messages['record_mesgs'][i].get('left_pco')}, right={test_messages['record_mesgs'][i].get('right_pco')}")
                            
                            # Check individual PCO fields
                            if 'left_pco' in record:
                                print(f"         Found left_pco: {record['left_pco']}")
                            else:
                                print(f"         ❌ left_pco missing")
                                
                            if 'right_pco' in record:
                                print(f"         Found right_pco: {record['right_pco']}")
                            else:
                                print(f"         ❌ right_pco missing")
                            
                            # Show numeric fields 
                            numeric_fields = [k for k, v in record.items() if isinstance(k, int)]
                            if numeric_fields:
                                print(f"       Numeric fields found: {numeric_fields}")
                                for nf in numeric_fields:
                                    print(f"         {nf}: {record[nf]}")
                
            else:
                print(f"   ❌ Decoding failed!")
                for error in errors:
                    print(f"     Error: {error}")
        
        except Exception as e:
            print(f"   Exception during decode: {e}")
            import traceback
            traceback.print_exc()
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    debug_decoding_process()