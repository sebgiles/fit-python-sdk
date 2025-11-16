#!/usr/bin/env python3
"""Debug specific field differences after fixing unknown message types"""

from garmin_fit_sdk import Decoder, Stream
from garmin_fit_sdk.encoder import Encoder

def debug_specific_field():
    fit_file = 'tests/fits/HrmPluginTestActivity.fit'
    
    print(f"=== Debugging auto_activity_detect field ===")
    
    # Decode original
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    messages, errors = decoder.read(preserve_invalid_values=True)
    
    # Find device_settings_mesgs
    if 'device_settings_mesgs' in messages:
        device_settings = messages['device_settings_mesgs'][0]
        print("Original device_settings_mesgs[0] fields:")
        for field, value in device_settings.items():
            print(f"  {field}: {value}")
    
    # Encode and decode
    encoder = Encoder(messages)
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp:
        temp_file = tmp.name
    
    try:
        success = encoder.write_to_file(temp_file)
        print(f"\nEncoder result: {success}")
        
        if success:
            # Decode back
            stream2 = Stream.from_file(temp_file)
            decoder2 = Decoder(stream2)
            roundtrip_messages, roundtrip_errors = decoder2.read(preserve_invalid_values=True)
            
            # Compare device_settings_mesgs
            if 'device_settings_mesgs' in roundtrip_messages:
                roundtrip_device_settings = roundtrip_messages['device_settings_mesgs'][0]
                print("\nRoundtrip device_settings_mesgs[0] fields:")
                for field, value in roundtrip_device_settings.items():
                    print(f"  {field}: {value}")
                
                # Find differences
                orig_fields = set(device_settings.keys())
                roundtrip_fields = set(roundtrip_device_settings.keys())
                
                missing = orig_fields - roundtrip_fields
                extra = roundtrip_fields - orig_fields
                
                print(f"\n📊 Field Analysis:")
                print(f"  Original fields: {len(orig_fields)}")
                print(f"  Roundtrip fields: {len(roundtrip_fields)}")
                print(f"  Missing fields: {missing}")
                print(f"  Extra fields: {extra}")
                
                # Check if auto_activity_detect exists and its value
                if 'auto_activity_detect' in device_settings:
                    orig_value = device_settings['auto_activity_detect']
                    print(f"\n🔍 auto_activity_detect original value: {orig_value} (type: {type(orig_value)})")
                    
                    # Check if it's getting filtered out during encoding
                    # Look at all numeric fields too
                    print(f"\n🔍 All numeric field keys in original:")
                    for field, value in device_settings.items():
                        if isinstance(field, int):
                            print(f"  {field}: {value}")
        
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_specific_field()