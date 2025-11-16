import pytest
from io import BytesIO
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.encoder import Encoder


class TestFieldProfileDebug:
    
    def test_debug_field_profile_lookup(self):
        """Debug whether software_version gets a proper field profile"""
        
        test_messages = {
            'device_info_mesgs': [{
                'manufacturer': 'development',
                'product': 0,
                'software_version': 1.0,
                'serial_number': 12345
            }]
        }
        
        # Debug the field definition creation
        original_write_message_definition = Encoder._write_message_definition
        
        def debug_write_message_definition(self, local_msg_num, global_msg_num, msg_profile, sample_message):
            print(f"DEBUG: Writing message definition for message: {sample_message.keys()}")
            print(f"  Message profile name: {msg_profile.get('name', 'UNKNOWN')}")
            print(f"  Available profile fields: {list(msg_profile.get('fields', {}).keys())}")
            
            # Check specifically for software_version
            for field_name in sample_message.keys():
                if field_name == 'software_version':
                    print(f"  Checking software_version field...")
                    
                    # Look for it in profile fields
                    profile_field = None
                    for field_num, field_profile in msg_profile['fields'].items():
                        if field_profile.get('name') == 'software_version':
                            profile_field = field_profile
                            break
                    
                    if profile_field:
                        print(f"    Found in profile: {profile_field}")
                    else:
                        print(f"    NOT FOUND in profile - will be synthetic")
            
            return original_write_message_definition(self, local_msg_num, global_msg_num, msg_profile, sample_message)
        
        # Monkey patch for debugging
        Encoder._write_message_definition = debug_write_message_definition
        
        try:
            encoder = Encoder(test_messages)
            encoded_bytes = encoder.write_to_bytes()
            
            # Decode and check result
            bytes_io = BytesIO(encoded_bytes)
            stream = Stream.from_bytes_io(bytes_io)
            decoder = Decoder(stream)
            decoded_messages, errors = decoder.read()
            
            assert len(errors) == 0
            decoded_value = decoded_messages['device_info_mesgs'][0].get('software_version')
            print(f"Final decoded value: {decoded_value}")
            
        finally:
            # Restore original method
            Encoder._write_message_definition = original_write_message_definition