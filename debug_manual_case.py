#!/usr/bin/env python3
"""Test if our simple manual test case causes decoder issues"""

import os
import tempfile
from garmin_fit_sdk import Decoder, Stream, Encoder

def test_simple_manual_case():
    """Test our simple manual test case that was failing"""
    
    test_messages = {
        'file_id_mesgs': [{
            'type': 'activity',
            'manufacturer': 'development',
            'product': 0,
            'serial_number': 12345,
            'time_created': 1000000000
        }],
        'record_mesgs': [
            # Record without PCO fields
            {
                'timestamp': 1000000000,
                'distance': 0,
                'speed': 5.0,
                'heart_rate': 120,
                'power': 200,
                'altitude': 100.0,
                'cadence': 90,
                'temperature': 25
            },
            # Record with PCO fields
            {
                'timestamp': 1000000001,
                'distance': 10,
                'speed': 5.2,
                'heart_rate': 125,
                'power': 210,
                'altitude': 101.0,
                'cadence': 92,
                'temperature': 25,
                'left_pco': -5,
                'right_pco': 3
            }
        ]
    }
    
    print("=== MANUAL TEST CASE ===")
    
    encoder = Encoder(test_messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        # Encode
        success = encoder.write_to_file(temp_path)
        print(f"Encoding success: {success}")
        
        file_size = os.path.getsize(temp_path)
        print(f"File size: {file_size} bytes")
        
        # Examine raw file
        with open(temp_path, 'rb') as f:
            data = f.read()
            print(f"Header: {data[:14].hex()}")
            print(f"First 30 data bytes: {data[14:44].hex()}")
        
        # Try to decode
        print(f"\nDecoding attempt:")
        try:
            stream = Stream.from_file(temp_path)
            decoder = Decoder(stream)
            
            # Check validity first
            stream.reset()
            print(f"Is FIT: {decoder.is_fit()}")
            
            stream.reset()
            print(f"Integrity OK: {decoder.check_integrity()}")
            
            # Decode
            stream.reset()
            messages, errors = decoder.read(
                expand_components=False,
                expand_sub_fields=False,
                merge_heart_rates=False
            )
            
            if errors:
                print(f"Decode errors: {errors}")
                
                # Let's try more verbose error info
                print("\nTrying again with detailed error tracking...")
                stream.reset()
                
                # Try decoding with different options
                for expand_comp in [False, True]:
                    for expand_sub in [False, True]:
                        for merge_hr in [False, True]:
                            try:
                                stream.reset()
                                msgs, errs = decoder.read(
                                    expand_components=expand_comp,
                                    expand_sub_fields=expand_sub,
                                    merge_heart_rates=merge_hr
                                )
                                if not errs:
                                    print(f"SUCCESS with: expand_comp={expand_comp}, expand_sub={expand_sub}, merge_hr={merge_hr}")
                                    print(f"  Got {len(msgs)} message types")
                                    return
                            except Exception as e:
                                pass
                
            else:
                print(f"Decode successful! Got {len(messages)} message types")
                for msg_type, msg_list in messages.items():
                    print(f"  {msg_type}: {len(msg_list)} messages")
                
                # Check if PCO fields are preserved
                if 'record_mesgs' in messages:
                    records = messages['record_mesgs']
                    for i, record in enumerate(records):
                        has_pco = 'left_pco' in record and 'right_pco' in record
                        print(f"    Record {i}: {len(record)} fields, PCO={has_pco}")
                        if has_pco:
                            print(f"      left_pco={record['left_pco']}, right_pco={record['right_pco']}")
                
        except Exception as e:
            print(f"Exception during decode: {e}")
            import traceback
            traceback.print_exc()
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    test_simple_manual_case()