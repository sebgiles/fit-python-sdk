#!/usr/bin/env python3

import sys
import tempfile
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.encoder import Encoder

def debug_field_definition_creation():
    """Debug exactly what fields are being included in message definitions"""
    fit_file = "tests/fits/WithGearChangeData.fit"
    
    # Get raw messages (no component expansion to get original structure)
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    stream.reset()
    
    raw_messages, _ = decoder.read(
        expand_components=False,
        expand_sub_fields=False,
        merge_heart_rates=False
    )
    
    print("=== FIELD DEFINITION ANALYSIS ===\n")
    
    if 'record_mesgs' in raw_messages:
        records = raw_messages['record_mesgs']
        
        print(f"Total records: {len(records)}")
        
        # Analyze field usage patterns
        print(f"\nFIELD USAGE PATTERNS:")
        print(f"Record[0] fields: {list(records[0].keys())}")
        print(f"Record[25] fields: {list(records[25].keys())}")
        
        # Check if ALL records have the same fields
        field_sets = []
        for i, record in enumerate(records[:50]):  # Check first 50
            field_set = set(k for k in record.keys() if not isinstance(k, int))
            field_sets.append((i, field_set))
        
        # Group by field set
        unique_field_sets = {}
        for i, field_set in field_sets:
            key = frozenset(field_set)
            if key not in unique_field_sets:
                unique_field_sets[key] = []
            unique_field_sets[key].append(i)
        
        print(f"\nUNIQUE FIELD PATTERNS (first 50 records):")
        for i, (field_set, record_indices) in enumerate(unique_field_sets.items()):
            print(f"  Pattern {i+1}: {len(record_indices)} records")
            print(f"    Fields: {sorted(field_set)}")
            print(f"    Records: {record_indices[:10]}{'...' if len(record_indices) > 10 else ''}")
        
        # Test encoding with raw messages
        print(f"\n=== ENCODING WITH RAW MESSAGES ===")
        
        encoder = Encoder(raw_messages)
        
        with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        result = encoder.write_to_file(temp_path)
        print(f"Encoding result: {result}")
        
        # Decode the result
        new_stream = Stream.from_file(temp_path)
        new_decoder = Decoder(new_stream)
        new_stream.reset()
        
        # Decode with same options (no expansion)
        new_messages, new_errors = new_decoder.read(
            expand_components=False,
            expand_sub_fields=False,
            merge_heart_rates=False
        )
        
        print(f"Re-decoding errors: {new_errors}")
        
        if 'record_mesgs' in new_messages:
            new_records = new_messages['record_mesgs']
            new_record_25 = new_records[25]
            
            print(f"\nORIGINAL record[25]: {list(records[25].keys())}")
            print(f"RE-DECODED record[25]: {list(new_record_25.keys())}")
            
            # Compare specific values
            for field in ['left_pco', 'right_pco', 'enhanced_respiration_rate']:
                orig = records[25].get(field, 'MISSING')
                new = new_record_25.get(field, 'MISSING')
                match = "✓" if orig == new else "✗"
                print(f"  {field}: {orig} -> {new} {match}")

if __name__ == "__main__":
    debug_field_definition_creation()