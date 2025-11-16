#!/usr/bin/env python3

import sys
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder

def test_raw_decoding():
    """Test decoding without component expansion to get original message structure"""
    fit_file = "tests/fits/WithGearChangeData.fit"
    
    print("=== TESTING RAW DECODING (no component expansion) ===\n")
    
    # Decode WITHOUT component expansion
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    stream.reset()
    
    # Disable component expansion to get raw fields
    raw_messages, raw_errors = decoder.read(
        expand_components=False,
        expand_sub_fields=False,
        merge_heart_rates=False
    )
    
    print(f"Raw decoding errors: {raw_errors}")
    
    if 'record_mesgs' in raw_messages:
        raw_record = raw_messages['record_mesgs'][25]
        print(f"\nRAW record[25] fields: {list(raw_record.keys())}")
        
        # Compare with expanded version
        stream.reset()
        expanded_messages, _ = decoder.read(expand_components=True)
        expanded_record = expanded_messages['record_mesgs'][25]
        
        print(f"EXPANDED record[25] fields: {list(expanded_record.keys())}")
        
        # Show differences
        raw_fields = set(k for k in raw_record.keys() if not isinstance(k, int))
        expanded_fields = set(k for k in expanded_record.keys() if not isinstance(k, int))
        
        missing_from_raw = expanded_fields - raw_fields
        extra_in_raw = raw_fields - expanded_fields
        
        print(f"\nFIELD DIFFERENCES:")
        print(f"  - Missing from raw (component fields): {missing_from_raw}")
        print(f"  - Extra in raw (parent fields): {extra_in_raw}")
        
        # Show specific field values
        print(f"\nFIELD VALUE COMPARISON:")
        
        target_fields = ['respiration_rate', 'enhanced_respiration_rate', 'left_pco', 'right_pco']
        for field in target_fields:
            raw_val = raw_record.get(field, 'NOT_PRESENT')
            exp_val = expanded_record.get(field, 'NOT_PRESENT') 
            print(f"  {field}: raw={raw_val}, expanded={exp_val}")

if __name__ == "__main__":
    test_raw_decoding()