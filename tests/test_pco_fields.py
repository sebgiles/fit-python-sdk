#!/usr/bin/env python3
"""Test PCO field encoding/decoding specifically"""

import os
import tempfile
import unittest
from garmin_fit_sdk import Decoder, Encoder


class TestPCOFields(unittest.TestCase):
    """Test that PCO fields are preserved through encode/decode cycles"""
    
    @classmethod
    def setUpClass(cls):
        """Load the test file with PCO fields"""
        test_file = '/home/seb/personal/strava/fit-python-sdk/tests/fits/WithGearChangeData.fit'
        cls.decoder = Decoder(test_file)
        cls.original_messages, cls.decode_errors = cls.decoder.read(
            expand_components=False,
            expand_sub_fields=False,
            merge_heart_rates=False
        )
        
        print(f"Original decode errors: {cls.decode_errors}")
        print(f"Original messages keys: {cls.original_messages.keys() if cls.original_messages else 'None'}")
        
        # Find a record with PCO fields
        cls.pco_record = None
        cls.pco_record_index = None
        
        if 'record_mesgs' in cls.original_messages:
            print(f"Found {len(cls.original_messages['record_mesgs'])} record messages")
            for i, record in enumerate(cls.original_messages['record_mesgs'][:10]):  # Check first 10
                print(f"Record {i}: {sorted(record.keys())}")
                if 'left_pco' in record and 'right_pco' in record:
                    cls.pco_record = record
                    cls.pco_record_index = i
                    break
                elif 'left_pco' in record or 'right_pco' in record:
                    print(f"  ^ Has partial PCO fields")
        else:
            print("No 'record_mesgs' key in original messages")
    
    def test_original_has_pco_fields(self):
        """Verify the original file contains PCO fields"""
        self.assertIsNotNone(self.pco_record, "Original file should contain records with PCO fields")
        self.assertIn('left_pco', self.pco_record, "Record should have left_pco field")
        self.assertIn('right_pco', self.pco_record, "Record should have right_pco field")
        
        print(f"Found PCO record at index {self.pco_record_index}:")
        print(f"  left_pco: {self.pco_record['left_pco']}")
        print(f"  right_pco: {self.pco_record['right_pco']}")
        print(f"  All fields: {sorted(self.pco_record.keys())}")
    
    def test_single_pco_record_encoding(self):
        """Test encoding/decoding a single record with PCO fields"""
        if self.pco_record is None:
            self.skipTest("No PCO record found in test data")
        
        # Create a minimal message set with just file_id and one PCO record
        minimal_messages = {
            'file_id_mesgs': self.original_messages['file_id_mesgs'],
            'record_mesgs': [self.pco_record]
        }
        
        # Encode the minimal message set
        encoder = Encoder()
        with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            success = encoder.encode_messages(temp_path, minimal_messages)
            self.assertTrue(success, "Encoding should succeed")
            
            # Decode the result
            decoder = Decoder(temp_path)
            new_messages, new_errors = decoder.read(
                expand_components=False,
                expand_sub_fields=False,
                merge_heart_rates=False
            )
            
            # Check for errors
            self.assertEqual(len(new_errors), 0, f"Decoding should not produce errors: {new_errors}")
            
            # Check that we have record messages
            self.assertIn('record_mesgs', new_messages, "Decoded messages should contain records")
            self.assertEqual(len(new_messages['record_mesgs']), 1, "Should have exactly one record")
            
            # Check PCO fields are preserved
            decoded_record = new_messages['record_mesgs'][0]
            self.assertIn('left_pco', decoded_record, "Decoded record should have left_pco field")
            self.assertIn('right_pco', decoded_record, "Decoded record should have right_pco field")
            
            # Check PCO values match
            self.assertEqual(decoded_record['left_pco'], self.pco_record['left_pco'], 
                           "left_pco value should be preserved")
            self.assertEqual(decoded_record['right_pco'], self.pco_record['right_pco'],
                           "right_pco value should be preserved")
            
            print("✓ Single PCO record encoding/decoding successful!")
            print(f"  Original left_pco: {self.pco_record['left_pco']}")
            print(f"  Decoded left_pco: {decoded_record['left_pco']}")
            print(f"  Original right_pco: {self.pco_record['right_pco']}")
            print(f"  Decoded right_pco: {decoded_record['right_pco']}")
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_multiple_record_encoding(self):
        """Test encoding multiple records with different field sets"""
        if self.pco_record is None:
            self.skipTest("No PCO record found in test data")
        
        # Get a few records including the PCO one and some without PCO
        records = self.original_messages['record_mesgs'][:5]  # First 5 records
        
        # Ensure our PCO record is included
        if self.pco_record not in records:
            records = records[:4] + [self.pco_record]
        
        test_messages = {
            'file_id_mesgs': self.original_messages['file_id_mesgs'],
            'record_mesgs': records
        }
        
        # Encode the messages
        encoder = Encoder()
        with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            success = encoder.encode_messages(temp_path, test_messages)
            self.assertTrue(success, "Encoding should succeed")
            
            # Decode the result
            decoder = Decoder(temp_path)
            new_messages, new_errors = decoder.read(
                expand_components=False,
                expand_sub_fields=False,
                merge_heart_rates=False
            )
            
            # Check for errors
            if new_errors:
                print(f"Decode errors: {new_errors}")
            
            # Check that we have record messages
            self.assertIn('record_mesgs', new_messages, "Decoded messages should contain records")
            self.assertEqual(len(new_messages['record_mesgs']), len(records), 
                           f"Should have {len(records)} records")
            
            # Find the PCO record in the decoded results
            decoded_pco_record = None
            for decoded_record in new_messages['record_mesgs']:
                if 'left_pco' in decoded_record and 'right_pco' in decoded_record:
                    # Check if values match our original
                    if (decoded_record['left_pco'] == self.pco_record['left_pco'] and
                        decoded_record['right_pco'] == self.pco_record['right_pco']):
                        decoded_pco_record = decoded_record
                        break
            
            self.assertIsNotNone(decoded_pco_record, 
                               "Should find a decoded record with matching PCO values")
            
            print("✓ Multiple record encoding/decoding successful!")
            print(f"  Encoded {len(records)} records")
            print(f"  Found PCO record with left_pco: {decoded_pco_record['left_pco']}, right_pco: {decoded_pco_record['right_pco']}")
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_field_pattern_analysis(self):
        """Analyze field patterns in record messages to understand variability"""
        if 'record_mesgs' not in self.original_messages:
            self.skipTest("No record messages found")
        
        records = self.original_messages['record_mesgs']
        
        # Analyze field patterns
        patterns = {}
        for i, record in enumerate(records):
            # Create field pattern (sorted field names)
            field_names = [name for name in record.keys() if not isinstance(name, int)]
            pattern = tuple(sorted(field_names))
            
            if pattern not in patterns:
                patterns[pattern] = {
                    'count': 0,
                    'indices': [],
                    'sample_record': record
                }
            patterns[pattern]['count'] += 1
            patterns[pattern]['indices'].append(i)
        
        print(f"\nFound {len(patterns)} different field patterns in {len(records)} records:")
        for i, (pattern, info) in enumerate(patterns.items()):
            print(f"  Pattern {i+1}: {info['count']} records, {len(pattern)} fields")
            print(f"    Fields: {list(pattern)}")
            print(f"    Sample indices: {info['indices'][:5]}{'...' if len(info['indices']) > 5 else ''}")
            
            # Check if this pattern has PCO fields
            has_pco = 'left_pco' in pattern and 'right_pco' in pattern
            if has_pco:
                print(f"    *** This pattern contains PCO fields ***")
            print()
        
        # This test always passes - it's just for analysis
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()