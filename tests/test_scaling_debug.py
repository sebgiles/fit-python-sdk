import pytest
from io import BytesIO
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.encoder import Encoder


class TestScalingDebug:
    
    def test_debug_software_version_encoding_process(self):
        """Debug what happens during software_version field encoding"""
        
        # Create a simple test with software_version
        test_messages = {
            'device_info_mesgs': [{
                'manufacturer': 'development',
                'product': 0,
                'software_version': 1.0,
                'serial_number': 12345
            }]
        }
        
        # Add debug to message data writing
        original_write_message_data = Encoder._write_message_data
        
        def debug_write_message_data(self, local_msg_num, msg_profile, message):
            print(f"DEBUG _write_message_data:")
            print(f"  Message: {message}")
            print(f"  Profile name: {msg_profile.get('name')}")
            print(f"  Profile fields keys: {list(msg_profile['fields'].keys()) if 'fields' in msg_profile else 'No fields'}")
            
            # Get field definitions
            msg_def = self._local_mesg_defs[local_msg_num]
            print(f"  Message def field_name_to_id: {msg_def.get('field_name_to_id', {})}")
            
            # Check field lookup for each field
            for field_def in msg_def['field_defs']:
                field_id = field_def['field_id']
                
                # Find field name using our mapping
                field_name = None
                for name, fid in msg_def.get('field_name_to_id', {}).items():
                    if fid == field_id:
                        field_name = name
                        break
                
                print(f"  Field ID {field_id} -> name: {field_name}")
                if field_name in message:
                    field_profile = msg_profile['fields'].get(field_name, {})
                    print(f"    Profile lookup result: {field_profile.get('name', 'NO NAME')} (keys: {list(field_profile.keys()) if field_profile else 'empty'})")
            
            return original_write_message_data(self, local_msg_num, msg_profile, message)
        
        # Monkey patch for debugging
        Encoder._write_message_data = debug_write_message_data
        
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
            Encoder._write_message_data = original_write_message_data