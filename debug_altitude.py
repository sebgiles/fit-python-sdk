#!/usr/bin/env python3
"""Debug the specific altitude field causing issues"""

from garmin_fit_sdk import Decoder, Stream, Encoder
import tempfile

def debug_altitude_issue():
    print("=== DEBUGGING ALTITUDE ISSUE ===")
    
    # Test ActivityDevFields.fit specifically
    stream = Stream.from_file("tests/fits/ActivityDevFields.fit")
    decoder = Decoder(stream)
    messages, _ = decoder.read()
    
    # Find the first record message with altitude
    first_record = None
    for msg in messages.get('record_mesgs', []):
        if 'altitude' in msg:
            first_record = msg
            break
    
    if first_record:
        print(f"First record altitude: {first_record['altitude']}")
        print(f"First record keys: {list(first_record.keys())}")
        
        # Check for multiple altitude-like fields
        altitude_fields = [k for k in first_record.keys() if 'altitude' in k.lower()]
        print(f"Altitude-like fields: {altitude_fields}")
        
        for field in altitude_fields:
            print(f"  {field}: {first_record[field]}")
    
    # Test encoding/decoding just this record
    test_messages = {'record_mesgs': [first_record]} if first_record else {}
    
    if test_messages:
        encoder = Encoder(test_messages)
        with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        result = encoder.write_to_file(temp_path)
        print(f"Encoding result: {result}")
        
        if result:
            new_stream = Stream.from_file(temp_path)
            new_decoder = Decoder(new_stream)
            new_messages, errors = new_decoder.read()
            
            print(f"Decoding errors: {len(errors)}")
            if errors:
                for error in errors:
                    print(f"  Error: {error}")
            
            if 'record_mesgs' in new_messages and len(new_messages['record_mesgs']) > 0:
                new_record = new_messages['record_mesgs'][0]
                print(f"Decoded altitude: {new_record.get('altitude', 'MISSING')}")
                
                # Compare all altitude fields
                for field in altitude_fields:
                    orig = first_record.get(field)
                    new_val = new_record.get(field, 'MISSING')
                    print(f"  {field}: {orig} -> {new_val}")

if __name__ == '__main__':
    debug_altitude_issue()