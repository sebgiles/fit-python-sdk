#!/usr/bin/env python3
"""Debug why auto_activity_detect field specifically gets lost"""

from garmin_fit_sdk import Decoder, Stream
from garmin_fit_sdk.encoder import Encoder

def debug_field_processing():
    fit_file = 'tests/fits/HrmPluginTestActivity.fit'
    
    print(f"=== Debugging auto_activity_detect field processing ===")
    
    # Decode original
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    messages, errors = decoder.read()
    
    # Create a minimal test case with just device_settings
    test_messages = {
        'file_id_mesgs': messages['file_id_mesgs'],
        'device_settings_mesgs': messages['device_settings_mesgs']
    }
    
    device_settings = test_messages['device_settings_mesgs'][0]
    print(f"Original auto_activity_detect: {device_settings.get('auto_activity_detect', 'NOT_FOUND')}")
    
    # Test encoding with minimal data
    encoder = Encoder(test_messages)
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp:
        temp_file = tmp.name
    
    try:
        # Enable debug output by adding some print statements temporarily
        success = encoder.write_to_file(temp_file)
        print(f"\nEncoder result: {success}")
        
        if success and os.path.exists(temp_file):
            # Decode back
            stream2 = Stream.from_file(temp_file)
            decoder2 = Decoder(stream2)
            roundtrip_messages, roundtrip_errors = decoder2.read()
            
            if 'device_settings_mesgs' in roundtrip_messages:
                roundtrip_device = roundtrip_messages['device_settings_mesgs'][0]
                print(f"Roundtrip auto_activity_detect: {roundtrip_device.get('auto_activity_detect', 'NOT_FOUND')}")
                
                # Check if the value 2147483647 appears as a numeric field
                for field, value in roundtrip_device.items():
                    if value == 2147483647:
                        print(f"Found value 2147483647 in field: {field}")
        
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_field_processing()