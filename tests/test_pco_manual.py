#!/usr/bin/env python3
"""Test PCO field encoding/decoding with known data"""

import os
import tempfile
import unittest
from garmin_fit_sdk import Decoder, Encoder


class TestPCOFieldsManual(unittest.TestCase):
    """Test PCO field encoding with manually created data"""
    
    def test_pco_encoding_with_manual_data(self):
        """Test encoding PCO fields with manually created message data"""
        
        # Create test messages with PCO fields manually
        # This simulates what we expect from a real file with PCO data
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
                },
                # Another record with different PCO values
                {
                    'timestamp': 1000000002,
                    'distance': 20,
                    'speed': 5.1,
                    'heart_rate': 123,
                    'power': 205,
                    'altitude': 102.0,
                    'cadence': 91,
                    'temperature': 24,
                    'left_pco': -7,
                    'right_pco': 2
                }
            ]
        }
        
        print(f"Creating test with {len(test_messages['record_mesgs'])} records")
        for i, record in enumerate(test_messages['record_mesgs']):
            has_pco = 'left_pco' in record and 'right_pco' in record
            print(f"  Record {i}: {len(record)} fields, PCO={has_pco}")
            if has_pco:
                print(f"    left_pco={record['left_pco']}, right_pco={record['right_pco']}")
        
        # Encode the test messages
        encoder = Encoder(test_messages)
        with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            print(f"\nEncoding to {temp_path}")
            success = encoder.write_to_file(temp_path)
            self.assertTrue(success, "Encoding should succeed")
            print("✓ Encoding successful")
            
            # Decode the result
            print("\nDecoding...")
            decoder = Decoder(temp_path)
            new_messages, new_errors = decoder.read(
                expand_components=False,
                expand_sub_fields=False,
                merge_heart_rates=False
            )
            
            # Check for errors
            if new_errors:
                print(f"Decode errors: {new_errors}")
            else:
                print("✓ No decode errors")
            
            # Check that we have record messages
            self.assertIn('record_mesgs', new_messages, "Decoded messages should contain records")
            decoded_records = new_messages['record_mesgs']
            print(f"✓ Decoded {len(decoded_records)} records")
            
            # Analyze each decoded record
            pco_found = False
            for i, decoded_record in enumerate(decoded_records):
                has_left = 'left_pco' in decoded_record
                has_right = 'right_pco' in decoded_record
                has_pco = has_left and has_right
                
                print(f"  Decoded record {i}: {len(decoded_record)} fields, PCO={has_pco}")
                print(f"    Fields: {sorted(decoded_record.keys())}")
                
                if has_pco:
                    pco_found = True
                    left_val = decoded_record['left_pco']
                    right_val = decoded_record['right_pco']
                    print(f"    PCO values: left_pco={left_val}, right_pco={right_val}")
                    
                    # Find matching original record
                    original_record = test_messages['record_mesgs'][i]
                    if 'left_pco' in original_record:
                        orig_left = original_record['left_pco']
                        orig_right = original_record['right_pco']
                        
                        self.assertEqual(left_val, orig_left, 
                                       f"Record {i}: left_pco should match ({left_val} != {orig_left})")
                        self.assertEqual(right_val, orig_right,
                                       f"Record {i}: right_pco should match ({right_val} != {orig_right})")
                        print(f"    ✓ PCO values match original")
                else:
                    # Check that records without PCO in original don't get PCO in decoded
                    original_record = test_messages['record_mesgs'][i]
                    orig_has_pco = 'left_pco' in original_record
                    if not orig_has_pco:
                        print(f"    ✓ No PCO fields (as expected)")
                    else:
                        self.fail(f"Record {i}: Original had PCO fields but decoded does not")
            
            self.assertTrue(pco_found, "At least one record should have PCO fields preserved")
            print(f"\n✓ All tests passed! PCO fields properly encoded and decoded.")
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_mixed_field_patterns(self):
        """Test that encoder handles multiple field patterns correctly"""
        
        # Create messages with very different field sets to test the encoder's
        # ability to handle variable field patterns
        test_messages = {
            'file_id_mesgs': [{
                'type': 'activity',
                'manufacturer': 'development',
                'product': 0,
                'time_created': 1000000000
            }],
            'record_mesgs': [
                # Minimal record
                {'timestamp': 1000000000, 'heart_rate': 120},
                
                # Record with power and cadence
                {'timestamp': 1000000001, 'heart_rate': 125, 'power': 200, 'cadence': 90},
                
                # Record with PCO fields
                {'timestamp': 1000000002, 'heart_rate': 130, 'power': 210, 
                 'left_pco': -4, 'right_pco': 6},
                
                # Record with different field combination
                {'timestamp': 1000000003, 'speed': 15.0, 'altitude': 500.0, 'temperature': 22},
                
                # Another PCO record with different fields
                {'timestamp': 1000000004, 'power': 180, 'cadence': 85, 
                 'left_pco': -8, 'right_pco': 1, 'temperature': 20}
            ]
        }
        
        print("\nTesting mixed field patterns:")
        for i, record in enumerate(test_messages['record_mesgs']):
            fields = sorted(record.keys())
            has_pco = 'left_pco' in record
            print(f"  Record {i}: {fields} (PCO: {has_pco})")
        
        # Encode
        encoder = Encoder(test_messages)
        with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            success = encoder.write_to_file(temp_path)
            self.assertTrue(success, "Encoding should succeed with mixed patterns")
            
            # Decode
            decoder = Decoder(temp_path)
            new_messages, new_errors = decoder.read(
                expand_components=False,
                expand_sub_fields=False,
                merge_heart_rates=False
            )
            
            self.assertEqual(len(new_errors), 0, f"Should have no decode errors: {new_errors}")
            self.assertIn('record_mesgs', new_messages)
            
            decoded_records = new_messages['record_mesgs']
            self.assertEqual(len(decoded_records), len(test_messages['record_mesgs']),
                           "Should decode same number of records")
            
            # Check that PCO records still have PCO fields
            pco_records_found = 0
            for i, (orig, decoded) in enumerate(zip(test_messages['record_mesgs'], decoded_records)):
                orig_has_pco = 'left_pco' in orig and 'right_pco' in orig
                decoded_has_pco = 'left_pco' in decoded and 'right_pco' in decoded
                
                if orig_has_pco:
                    pco_records_found += 1
                    self.assertTrue(decoded_has_pco, 
                                   f"Record {i}: Original had PCO but decoded doesn't")
                    self.assertEqual(decoded['left_pco'], orig['left_pco'],
                                   f"Record {i}: left_pco mismatch")
                    self.assertEqual(decoded['right_pco'], orig['right_pco'],
                                   f"Record {i}: right_pco mismatch")
                    print(f"  ✓ Record {i}: PCO preserved ({orig['left_pco']}, {orig['right_pco']})")
            
            self.assertGreater(pco_records_found, 0, "Should have found PCO records")
            print(f"✓ All {pco_records_found} PCO records preserved correctly")
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()