#!/usr/bin/env python3
"""Analyze the ignored fields to understand what's wrong"""

from garmin_fit_sdk import Decoder, Stream, Encoder
import tempfile
import os

def analyze_ignored_fields():
    print("=== ANALYZING IGNORED FIELDS ===")
    
    # Test files to check
    files = [
        "tests/fits/ActivityDevFields.fit",
        "tests/fits/HrmPluginTestActivity.fit", 
        "tests/fits/WithGearChangeData.fit"
    ]
    
    ignored_fields = [
        'left_power_phase', 
        'right_power_phase', 
        'left_power_phase_peak',
        'right_power_phase_peak',
        'left_right_balance',
        'event_group',
        'manufacturer',
        'developer_fields',
    ]
    
    for filepath in files:
        print(f"\n=== {os.path.basename(filepath)} ===")
        
        # Decode original
        stream = Stream.from_file(filepath)
        decoder = Decoder(stream)
        original_messages, _ = decoder.read()
        
        # Check which ignored fields are actually present
        found_fields = set()
        field_examples = {}
        
        for msg_type, messages in original_messages.items():
            for msg in messages:
                for field_name, field_value in msg.items():
                    if field_name in ignored_fields:
                        found_fields.add(field_name)
                        if field_name not in field_examples:
                            field_examples[field_name] = []
                        if len(field_examples[field_name]) < 3:
                            field_examples[field_name].append(field_value)
        
        print(f"Found ignored fields: {sorted(found_fields)}")
        for field_name, examples in field_examples.items():
            print(f"  {field_name}: {examples}")
        
        if found_fields:
            # Test encoding with these fields
            print(f"Testing encoding with ignored fields...")
            
            encoder = Encoder(original_messages)
            with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            try:
                result = encoder.write_to_file(temp_path)
                print(f"Encoding success: {result}")
                
                if result:
                    # Try decoding
                    new_stream = Stream.from_file(temp_path)
                    new_decoder = Decoder(new_stream)
                    new_messages, new_errors = new_decoder.read()
                    
                    print(f"Decoding errors: {len(new_errors)}")
                    
                    # Check what happened to the ignored fields
                    for field_name in found_fields:
                        orig_count = 0
                        new_count = 0
                        mismatches = 0
                        
                        for msg_type in original_messages:
                            if msg_type in new_messages:
                                for orig_msg, new_msg in zip(original_messages[msg_type], new_messages[msg_type]):
                                    if field_name in orig_msg:
                                        orig_count += 1
                                        if field_name in new_msg:
                                            new_count += 1
                                            if orig_msg[field_name] != new_msg[field_name]:
                                                mismatches += 1
                                                if mismatches <= 3:  # Show first few mismatches
                                                    print(f"    {field_name} mismatch: {orig_msg[field_name]} -> {new_msg[field_name]}")
                        
                        print(f"  {field_name}: {orig_count} original -> {new_count} new, {mismatches} mismatches")
            
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

if __name__ == '__main__':
    analyze_ignored_fields()