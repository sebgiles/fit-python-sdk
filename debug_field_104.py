#!/usr/bin/env python3

from garmin_fit_sdk import Decoder, Stream, Encoder, profile
import tempfile
import os

def debug_field_104():
    print("=== Debugging Field 104 Array Padding ===")
    
    # Read original file
    original_stream = Stream.from_file('tests/fits/HrmPluginTestActivity.fit')
    decoder = Decoder(original_stream)
    
    original_messages, _ = decoder.read(
        preserve_invalid_values=True,
        merge_heart_rates=False,
        expand_sub_fields=False,
        expand_components=False
    )
    
    if 'device_settings_mesgs' in original_messages and original_messages['device_settings_mesgs']:
        orig_msg = original_messages['device_settings_mesgs'][0]
        print(f"Original field 104: {orig_msg.get(104, 'NOT FOUND')}")
        print(f"Original field 104 type: {type(orig_msg.get(104, 'NOT FOUND'))}")
        
        # Check profile info for field 104 in device_settings
        print(f"\nLooking up field 104 in FIT profile...")
        
        # Find device_settings message in profile  
        for msg_num, msg_profile in profile.Profile['messages'].items():
            if msg_profile.get('name') == 'device_settings':
                print(f"Found device_settings message (num {msg_num})")
                
                if 104 in msg_profile.get('fields', {}):
                    field_profile = msg_profile['fields'][104]
                    print(f"Field 104 profile: {field_profile}")
                else:
                    print(f"Field 104 not found in profile fields")
                    print(f"Available fields: {list(msg_profile.get('fields', {}).keys())}")
                break
    
    # Encode and decode back
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        encoder = Encoder(original_messages)
        encoder.write_to_file(tmp_path)
        
        # Decode result
        new_stream = Stream.from_file(tmp_path)
        new_decoder = Decoder(new_stream)
        new_messages, _ = new_decoder.read(
            preserve_invalid_values=True,
            merge_heart_rates=False,
            expand_sub_fields=False,
            expand_components=False
        )
        
        if 'device_settings_mesgs' in new_messages and new_messages['device_settings_mesgs']:
            new_msg = new_messages['device_settings_mesgs'][0]
            print(f"\nAfter roundtrip field 104: {new_msg.get(104, 'NOT FOUND')}")
            print(f"After roundtrip field 104 type: {type(new_msg.get(104, 'NOT FOUND'))}")
            
            # Compare arrays element by element
            if 104 in orig_msg and 104 in new_msg:
                orig_arr = orig_msg[104]
                new_arr = new_msg[104]
                print(f"\nArray comparison:")
                print(f"Original length: {len(orig_arr)}")
                print(f"New length: {len(new_arr)}")
                
                for i, (orig_val, new_val) in enumerate(zip(orig_arr, new_arr)):
                    if orig_val != new_val:
                        print(f"  Index {i}: {orig_val} -> {new_val}")
                        if i >= 10:  # Don't spam too much
                            print(f"  ... (more differences)")
                            break
    
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

if __name__ == "__main__":
    debug_field_104()