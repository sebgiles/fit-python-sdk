'''encoder.py: Contains the encoder class which is used to encode fit files.'''

import struct
from . import CrcCalculator
from . import fit as FIT
from .profile import Profile


class Encoder:
    '''
    A class for encoding messages into a FIT file format.

    Attributes:
        _messages: The messages to be encoded into FIT format.
    '''

    def __init__(self, messages: dict):
        if messages is None:
            raise RuntimeError("FIT Runtime Error messages parameter is None.")
        
        self._messages = messages
        self._local_mesg_defs = {}  # Track message definitions we've written
        self._data_buffer = bytearray()

    def write_to_file(self, filename: str) -> bool:
        '''
        Writes the messages to a FIT file.
        
        Args:
            filename: The path where the FIT file should be written
            
        Returns:
            bool: True if successful, False otherwise
        '''
        try:
            data = self.write_to_bytes()
            with open(filename, 'wb') as f:
                f.write(data)
            return True
        except Exception as e:
            # For debugging, let's see what the error is
            import traceback
            print(f"Encoder error: {e}")
            traceback.print_exc()
            return False

    def write_to_bytes(self) -> bytearray:
        '''
        Writes the messages to a bytearray in FIT format.
        
        Returns:
            bytearray: The encoded FIT data
        '''
        # Clear any previous data
        self._data_buffer = bytearray()
        self._local_mesg_defs = {}
        
        # Write all messages to data buffer
        self._write_messages()
        
        # Create header
        header = self._create_header(len(self._data_buffer))
        
        # Calculate CRC for the entire file
        file_data = header + self._data_buffer
        crc = CrcCalculator.calculate_crc(file_data, 0, len(file_data))
        crc_bytes = struct.pack('<H', crc)
        
        return header + self._data_buffer + crc_bytes

    def _create_header(self, data_size: int) -> bytearray:
        '''Create the FIT file header'''
        header = bytearray()
        
        # Header size (14 bytes with CRC)
        header.append(14)
        
        # Protocol version (2.0)
        header.append(0x20)
        
        # Profile version (21.178)
        profile_version = 21178
        header.extend(struct.pack('<H', profile_version))
        
        # Data size
        header.extend(struct.pack('<L', data_size))
        
        # Data type (".FIT")
        header.extend(b'.FIT')
        
        # Calculate header CRC (first 12 bytes)
        header_crc = CrcCalculator.calculate_crc(header, 0, 12)
        header.extend(struct.pack('<H', header_crc))
        
        return header

    def _write_messages(self):
        '''Write all messages to the data buffer'''
        # Write file_id message first (required by FIT spec)
        if 'file_id_mesgs' in self._messages:
            self._write_message_type('file_id_mesgs', 0)
        
        # Write all other message types
        for msg_type, messages in self._messages.items():
            if msg_type != 'file_id_mesgs' and messages:
                # Look up global message number from profile
                global_msg_num = self._get_global_message_number(msg_type)
                if global_msg_num is not None:
                    self._write_message_type(msg_type, global_msg_num)

    def _write_message_type(self, msg_type: str, global_msg_num: int):
        '''Write all messages of a specific type'''
        messages = self._messages[msg_type]
        if not messages:
            return
            
        # Get message definition from profile
        if global_msg_num in Profile['messages']:
            msg_profile = Profile['messages'][global_msg_num]
        else:
            return  # Skip unknown message types for now
        
        # Assign local message number
        local_msg_num = len(self._local_mesg_defs) % 16
        
        # Write message definition
        self._write_message_definition(local_msg_num, global_msg_num, msg_profile, messages[0])
        
        # Write all messages of this type
        for message in messages:
            self._write_message_data(local_msg_num, msg_profile, message)

    def _write_message_definition(self, local_msg_num: int, global_msg_num: int, msg_profile: dict, sample_message: dict):
        '''Write a message definition record'''
        # Record header byte (0x40 = definition message)
        record_header = 0x40 | (local_msg_num & 0x0F)
        self._data_buffer.append(record_header)
        
        # Reserved byte
        self._data_buffer.append(0)
        
        # Architecture (0 = little endian)
        self._data_buffer.append(0)
        
        # Global message number
        self._data_buffer.extend(struct.pack('<H', global_msg_num))
        
        # Build field definitions based on sample message
        field_defs = []
        for field_name, field_value in sample_message.items():
            if field_name in msg_profile['fields']:
                field_profile = msg_profile['fields'][field_name]
            else:
                # Try to find field by name
                field_profile = None
                for field_id, fp in msg_profile['fields'].items():
                    if fp['name'] == field_name:
                        field_profile = fp
                        break
                
                if field_profile is None:
                    continue  # Skip unknown fields
            
            # Determine field size and base type
            base_type, size = self._determine_field_type_and_size(field_profile, field_value)
            
            field_defs.append({
                'field_id': field_profile['num'],
                'size': size,
                'base_type': base_type
            })
        
        # Number of fields
        self._data_buffer.append(len(field_defs))
        
        # Field definitions
        for field_def in field_defs:
            self._data_buffer.append(field_def['field_id'])
            self._data_buffer.append(field_def['size'])
            self._data_buffer.append(field_def['base_type'])
        
        # Store definition for later use
        self._local_mesg_defs[local_msg_num] = {
            'global_msg_num': global_msg_num,
            'profile': msg_profile,
            'field_defs': field_defs
        }

    def _write_message_data(self, local_msg_num: int, msg_profile: dict, message: dict):
        '''Write a message data record'''
        # Record header (normal message)
        record_header = local_msg_num & 0x0F
        self._data_buffer.append(record_header)
        
        # Get field definitions
        msg_def = self._local_mesg_defs[local_msg_num]
        
        # Write field data in the order defined in the message definition
        for field_def in msg_def['field_defs']:
            field_id = field_def['field_id']
            
            # Find field name
            field_name = None
            for fname, fvalue in message.items():
                if fname in msg_profile['fields'] and msg_profile['fields'][fname]['num'] == field_id:
                    field_name = fname
                    break
                # Also try direct field ID lookup
                elif field_id in msg_profile['fields'] and msg_profile['fields'][field_id]['name'] == fname:
                    field_name = fname
                    break
            
            if field_name is None or field_name not in message:
                # Write invalid/default value
                invalid_value = FIT.BASE_TYPE_DEFINITIONS[field_def['base_type']]['invalid']
                self._write_field_bytes(invalid_value, field_def['size'], field_def['base_type'])
            else:
                # Write actual field value
                field_value = message[field_name]
                self._write_field_value(field_value, field_def['size'], field_def['base_type'], msg_profile['fields'].get(field_name, {}))

    def _write_field_value(self, value, size: int, base_type: int, field_profile: dict):
        '''Write a field value with proper encoding'''
        base_type_def = FIT.BASE_TYPE_DEFINITIONS[base_type]
        
        if base_type == FIT.BASE_TYPE['STRING']:
            # String field
            if isinstance(value, str):
                string_bytes = value.encode('utf-8')
                # Pad or truncate to fit size
                if len(string_bytes) < size:
                    string_bytes += b'\x00' * (size - len(string_bytes))
                else:
                    string_bytes = string_bytes[:size-1] + b'\x00'
                self._data_buffer.extend(string_bytes[:size])
            else:
                # Invalid string, write nulls
                self._data_buffer.extend(b'\x00' * size)
        
        elif isinstance(value, (list, tuple)):
            # Array field
            element_size = base_type_def['size']
            num_elements = size // element_size
            for i in range(num_elements):
                if i < len(value):
                    self._write_single_value(value[i], base_type, field_profile)
                else:
                    self._write_single_value(base_type_def['invalid'], base_type, field_profile)
        
        else:
            # Single value
            self._write_single_value(value, base_type, field_profile)

    def _write_single_value(self, value, base_type: int, field_profile: dict):
        '''Write a single value with proper type conversion'''
        from . import util
        import datetime
        
        base_type_def = FIT.BASE_TYPE_DEFINITIONS[base_type]
        type_code = base_type_def['type_code']
        
        # Convert value if needed
        if value is None:
            value = base_type_def['invalid']
        
        # Handle datetime objects - convert back to FIT timestamp
        if isinstance(value, datetime.datetime):
            # Convert datetime back to FIT timestamp (seconds since FIT epoch)
            # FIT epoch is 1989-12-31 00:00:00 UTC
            fit_timestamp = int(value.timestamp()) - util.FIT_EPOCH_S
            value = fit_timestamp
        
        # Apply reverse scale and offset if we have profile info
        if field_profile and 'scale' in field_profile and 'offset' in field_profile:
            if len(field_profile['scale']) == 1 and len(field_profile['offset']) == 1:
                scale = field_profile['scale'][0]
                offset = field_profile['offset'][0]
                if scale != 1 or offset != 0:
                    # Reverse the decoder's operation: (value + offset) * scale
                    value = int((value + offset) * scale)
        
        # Convert strings back to numbers if needed
        if isinstance(value, str) and base_type != FIT.BASE_TYPE['STRING']:
            # Try to convert string enum values back to numbers
            if field_profile and 'type' in field_profile:
                field_type = field_profile['type']
                if field_type in Profile['types']:
                    # Find the numeric value for this string
                    for num_val, str_val in Profile['types'][field_type].items():
                        if str_val == value:
                            value = int(num_val)
                            break
                    else:
                        value = base_type_def['invalid']
        
        # Pack the value
        try:
            if type_code in ['b', 'B']:
                packed = struct.pack('<' + type_code, int(value) & 0xFF)
            elif type_code in ['h', 'H']:
                packed = struct.pack('<' + type_code, int(value) & 0xFFFF)
            elif type_code in ['i', 'I', 'l', 'L']:
                packed = struct.pack('<' + type_code, int(value) & 0xFFFFFFFF)
            elif type_code in ['q', 'Q']:
                packed = struct.pack('<' + type_code, int(value))
            elif type_code in ['f', 'd']:
                packed = struct.pack('<' + type_code, float(value))
            else:
                packed = struct.pack('<B', base_type_def['invalid'])
            
            self._data_buffer.extend(packed)
        except (struct.error, ValueError, OverflowError):
            # If packing fails, write invalid value
            self._write_field_bytes(base_type_def['invalid'], base_type_def['size'], base_type)

    def _write_field_bytes(self, value, size: int, base_type: int):
        '''Write raw bytes for a field'''
        base_type_def = FIT.BASE_TYPE_DEFINITIONS[base_type]
        type_code = base_type_def['type_code']
        
        try:
            if size == 1:
                packed = struct.pack('<B', int(value) & 0xFF)
            elif size == 2:
                packed = struct.pack('<H', int(value) & 0xFFFF)
            elif size == 4:
                packed = struct.pack('<L', int(value) & 0xFFFFFFFF)
            elif size == 8:
                packed = struct.pack('<Q', int(value))
            else:
                packed = bytes([int(value) & 0xFF] * size)
            
            self._data_buffer.extend(packed)
        except (struct.error, ValueError):
            self._data_buffer.extend(b'\xFF' * size)

    def _determine_field_type_and_size(self, field_profile: dict, field_value) -> tuple:
        '''Determine the base type and size for a field'''
        if 'type' in field_profile and field_profile['type'] in FIT.FIELD_TYPE_TO_BASE_TYPE:
            base_type = FIT.FIELD_TYPE_TO_BASE_TYPE[field_profile['type']]
            base_type_def = FIT.BASE_TYPE_DEFINITIONS[base_type]
            
            if isinstance(field_value, (list, tuple)):
                # Array field
                size = len(field_value) * base_type_def['size']
            else:
                # Single field
                size = base_type_def['size']
            
            return base_type, size
        else:
            # Default to appropriate type based on value
            if isinstance(field_value, str):
                return FIT.BASE_TYPE['STRING'], min(len(field_value) + 1, 255)
            elif isinstance(field_value, bool):
                return FIT.BASE_TYPE['UINT8'], 1
            elif isinstance(field_value, float):
                return FIT.BASE_TYPE['FLOAT32'], 4
            elif isinstance(field_value, int):
                if -128 <= field_value <= 127:
                    return FIT.BASE_TYPE['SINT8'], 1
                elif 0 <= field_value <= 255:
                    return FIT.BASE_TYPE['UINT8'], 1
                elif -32768 <= field_value <= 32767:
                    return FIT.BASE_TYPE['SINT16'], 2
                elif 0 <= field_value <= 65535:
                    return FIT.BASE_TYPE['UINT16'], 2
                elif -2147483648 <= field_value <= 2147483647:
                    return FIT.BASE_TYPE['SINT32'], 4
                else:
                    return FIT.BASE_TYPE['UINT32'], 4
            elif isinstance(field_value, (list, tuple)):
                if field_value:
                    elem_type, elem_size = self._determine_field_type_and_size({}, field_value[0])
                    return elem_type, len(field_value) * elem_size
                else:
                    return FIT.BASE_TYPE['UINT8'], 1
            else:
                return FIT.BASE_TYPE['UINT8'], 1

    def _get_global_message_number(self, msg_type: str) -> int:
        '''Get the global message number for a message type'''
        for global_num, msg_info in Profile['messages'].items():
            if msg_info.get('messages_key') == msg_type:
                return global_num
        return None