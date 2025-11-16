'''encoder.py: Contains the encoder class which is used to encode fit files.'''

import struct
import datetime
from . import CrcCalculator
from . import fit as FIT
from . import util
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
        header.append(0x02)
        
        # Profile version (21.173 to match original)
        profile_version = 21173
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
            self._write_message_type(0, self._messages['file_id_mesgs'])
        
        # Write all other message types
        for msg_type, messages in self._messages.items():
            if msg_type != 'file_id_mesgs' and messages:
                # Look up global message number from profile
                global_msg_num = self._get_global_message_number(msg_type)
                if global_msg_num is not None:
                    self._write_message_type(global_msg_num, messages)

    def _write_message_type(self, message_type_num: int, messages: list):
        '''Write all messages of a specific type, creating individual definitions for each unique field set'''
        msg_profile = Profile['messages'][message_type_num]
        global_msg_num = message_type_num
        
        # Track which messages we've processed with each definition
        definition_cache = {}  # field_set_hash -> local_msg_num
        
        for message in messages:
            # Skip 'mesg_num' as it's metadata
            message_fields = set(field for field in message.keys() if field != 'mesg_num')
            
            # Create a hash of the field set to identify identical field combinations
            field_set_hash = hash(frozenset(message_fields))
            
            if field_set_hash in definition_cache:
                # Reuse existing definition
                local_msg_num = definition_cache[field_set_hash]
            else:
                # Create a new definition for this field combination
                local_msg_num = len(self._local_mesg_defs) % 16
                definition_cache[field_set_hash] = local_msg_num
                
                # Write message definition for this specific field combination
                self._write_specific_message_definition(local_msg_num, global_msg_num, msg_profile, message_fields, message)
            
            # Write the message data using the appropriate definition
            self._write_message_data(local_msg_num, msg_profile, message)

    def _get_message_field_pattern(self, message: dict) -> frozenset:
        '''Get field pattern for a message to enable grouping by field combinations'''
        return pattern_groups
    
    def _get_message_field_pattern(self, message: dict) -> frozenset:
        '''Get the field pattern (signature) for a message'''
        # Create a signature based on non-null field names (excluding numeric field IDs)
        field_names = set()
        for field_name, field_value in message.items():
            if not isinstance(field_name, int) and field_value is not None:
                field_names.add(field_name)
        
        return frozenset(field_names)

    def _write_message_definition(self, local_msg_num: int, global_msg_num: int, msg_profile: dict, pattern_messages: list):
        '''Write a message definition record for a specific field pattern'''
        # Record header byte (0x40 = definition message)
        record_header = 0x40 | (local_msg_num & 0x0F)
        self._data_buffer.append(record_header)
        
        # Reserved byte
        self._data_buffer.append(0)
        
        # Architecture (0 = little endian)
        self._data_buffer.append(0)
        
        # Global message number
        self._data_buffer.extend(struct.pack('<H', global_msg_num))
        
        # Use the field pattern from the first message in this group
        # All messages in pattern_messages have the same field pattern
        sample_message = pattern_messages[0]
        field_names = [name for name, value in sample_message.items() 
                      if not isinstance(name, int) and value is not None]
        
        # Build field definitions for this specific pattern
        field_defs = []
        field_name_to_id = {}
        
        print(f"DEBUG: Creating definition for pattern with {len(field_names)} fields: {sorted(field_names)}")
        
        for field_name in sorted(field_names):  # Sort for consistent output            
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
                    # Skip unknown fields that aren't in the profile
                    # This prevents synthetic fields that the decoder can't understand
                    print(f"DEBUG: Skipping unknown field {field_name}")
                    continue
            
            # Store the field name to ID mapping
            field_name_to_id[field_name] = field_profile['num']
            
            # Determine field size and base type from sample message
            sample_value = sample_message[field_name]
            base_type, size = self._determine_field_type_and_size(field_profile, sample_value)
            
            field_defs.append({
                'field_id': field_profile['num'],
                'size': size,
                'base_type': base_type
            })
        
        print(f"DEBUG: Created {len(field_defs)} field definitions for local message {local_msg_num}")
        
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
            'field_defs': field_defs,
            'field_name_to_id': field_name_to_id
        }

    def _write_specific_message_definition(self, local_msg_num: int, global_msg_num: int, msg_profile, message_fields: set, sample_message: dict):
        '''Write a message definition for a specific set of fields'''
        # Definition header: 0100xxxx where xxxx is local message number
        definition_header = 0x40 | (local_msg_num & 0x0F)
        self._data_buffer.append(definition_header)
        
        # Reserved byte
        self._data_buffer.append(0)
        
        # Architecture
        self._data_buffer.append(0)  # Definition & Data Messages are little endian
        
        # Global message number (2 bytes, little endian)
        self._data_buffer.extend(struct.pack('<H', global_msg_num))
        
        # Create field definitions for the specific fields in this message
        field_defs = []
        field_name_to_id = {}
        
        # Use the sample message values for type determination
        sample_values = sample_message
        
        # Separate string field names from numeric developer field numbers  
        string_fields = [f for f in message_fields if isinstance(f, str)]
        numeric_fields = [f for f in message_fields if isinstance(f, int)]
        
        # Process string fields first (regular fields)
        for field_name in sorted(string_fields):  # Sort for consistent output            
            if 'fields' in msg_profile:
                # Look for field by name in the fields dict
                field_profile = None
                for field_info in msg_profile['fields'].values():
                    if field_info['name'] == field_name:
                        field_profile = field_info
                        break
                
                if field_profile is not None:
                    field_id = field_profile['num']
                    field_name_to_id[field_name] = field_id
                    
                    # Determine base type and size using existing method
                    sample_value = sample_values.get(field_name)
                    if sample_value is not None:
                        base_type, size = self._determine_field_type_and_size(field_profile, sample_value)
                    else:
                        # Fallback to reasonable defaults based on field type
                        fit_type = field_profile.get('type', 'uint8')
                        if fit_type == 'string':
                            base_type, size = FIT.BASE_TYPE['STRING'], 1
                        elif fit_type in FIT.BASE_TYPE:
                            base_type = FIT.BASE_TYPE[fit_type]
                            size = 1  # Default size
                        else:
                            base_type, size = FIT.BASE_TYPE['UINT8'], 1
                    
                    field_defs.append({
                        'field_id': field_id,
                        'size': size,
                        'base_type': base_type
                    })
        
        # Process numeric fields (developer fields)
        for field_num in sorted(numeric_fields):
            # Find a sample value to determine type and size
            sample_value = sample_values.get(field_num)
            if sample_value is not None:
                # For arrays, check if they contain only None values
                if isinstance(sample_value, list):
                    # Skip arrays that are entirely None or mostly None
                    non_none_count = sum(1 for v in sample_value if v is not None)
                    if non_none_count == 0:
                        print(f"DEBUG: Skipping numeric field {field_num} - array is entirely None")
                        continue
                    # Use the first non-None value as sample for type determination
                    for val in sample_value:
                        if val is not None:
                            sample_value = val
                            break
                
                base_type, size = self._determine_field_type_and_size(None, sample_value)
                
                # Calculate correct size for arrays
                original_sample = sample_values.get(field_num)
                if isinstance(original_sample, list):
                    size = len(original_sample) * FIT.BASE_TYPE_DEFINITIONS[base_type]['size']
                
                field_defs.append({
                    'field_id': field_num,
                    'size': size, 
                    'base_type': base_type
                })
                field_name_to_id[field_num] = field_num
        
        # Number of fields (1 byte)
        self._data_buffer.append(len(field_defs))
        
        # Field definitions (3 bytes each)
        for field_def in field_defs:
            self._data_buffer.append(field_def['field_id'])  # Field definition number
            self._data_buffer.append(field_def['size'])       # Size in bytes
            self._data_buffer.append(field_def['base_type'])  # Base type
        
        # Store the definition for later use when writing message data
        self._local_mesg_defs[local_msg_num] = {
            'global_msg_num': global_msg_num,
            'field_defs': field_defs,
            'field_name_to_id': field_name_to_id
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
            
            # Find field name using our mapping
            field_name = None
            for name, fid in msg_def.get('field_name_to_id', {}).items():
                if fid == field_id:
                    field_name = name
                    break
            
            # Fallback to profile lookup if not found in our mapping
            if field_name is None:
                for fname, fvalue in message.items():
                    if fname in msg_profile['fields'] and msg_profile['fields'][fname]['num'] == field_id:
                        field_name = fname
                        break
            
            if field_name is None or field_name not in message:
                # Write invalid/default value
                invalid_value = FIT.BASE_TYPE_DEFINITIONS[field_def['base_type']]['invalid']
                self._write_field_bytes(invalid_value, field_def['size'], field_def['base_type'])
            else:
                # Write actual field value
                field_value = message[field_name]
                # Look up field profile by searching for the field with matching name
                field_profile = {}
                for fid, finfo in msg_profile['fields'].items():
                    if finfo.get('name') == field_name:
                        field_profile = finfo
                        break
                self._write_field_value(field_value, field_def['size'], field_def['base_type'], field_profile)

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
        '''Write a single field value'''
        
        base_type_def = FIT.BASE_TYPE_DEFINITIONS[base_type]
        type_code = base_type_def['type_code']
        
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
                    # Only apply scaling to numeric values, not None
                    if value is not None:
                        # The correct formula depends on whether there's an offset
                        if offset == 0:
                            # For zero offset: decoder = raw / scale, so encoder = actual * scale
                            value = round(value * scale)
                        else:
                            # For non-zero offset: decoder = (raw / scale) + offset, so encoder = (actual - offset) * scale
                            value = round((value - offset) * scale)
        
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
            # Handle None values
            if value is None:
                self._write_field_bytes(base_type_def['invalid'], base_type_def['size'], base_type)
                return
                
            if type_code == 'b':  # signed byte
                packed = struct.pack('<b', int(value))
            elif type_code == 'B':  # unsigned byte
                packed = struct.pack('<B', int(value) & 0xFF)
            elif type_code == 'h':  # signed short
                packed = struct.pack('<h', int(value))
            elif type_code == 'H':  # unsigned short
                packed = struct.pack('<H', int(value) & 0xFFFF)
            elif type_code in ['i', 'I', 'l', 'L']:
                packed = struct.pack('<' + type_code, int(value) & 0xFFFFFFFF)
            elif type_code in ['q', 'Q']:
                packed = struct.pack('<' + type_code, int(value))
            elif type_code in ['f', 'd']:
                packed = struct.pack('<' + type_code, float(value))
            else:
                packed = struct.pack('<B', base_type_def['invalid'])
            
            self._data_buffer.extend(packed)
        except (struct.error, ValueError, OverflowError, TypeError):
            # If packing fails, write invalid value
            self._write_field_bytes(base_type_def['invalid'], base_type_def['size'], base_type)

    def _write_field_bytes(self, value, size: int, base_type: int):
        '''Write raw bytes for a field'''
        # Defensive check for base_type
        if base_type is None or base_type not in FIT.BASE_TYPE_DEFINITIONS:
            # Fallback to UINT8 if base_type is invalid
            base_type = FIT.BASE_TYPE['UINT8']
            
        base_type_def = FIT.BASE_TYPE_DEFINITIONS[base_type]
        type_code = base_type_def['type_code']
        
        try:
            # Handle None values defensively
            if value is None:
                # Use the base type's invalid value
                value = base_type_def['invalid']
            
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
        
        # Handle developer fields (when field_profile is None)
        if field_profile is None:
            # For developer fields, infer type from the value
            if isinstance(field_value, str):
                size = len(field_value) + 1  # Include null terminator
                return FIT.BASE_TYPE['STRING'], size
            elif isinstance(field_value, bool):
                return FIT.BASE_TYPE['ENUM'], 1
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
            elif isinstance(field_value, float):
                return FIT.BASE_TYPE['FLOAT32'], 4
            else:
                # Default fallback
                return FIT.BASE_TYPE['UINT8'], 1
        
        # Convert enum string values to numbers first
        if isinstance(field_value, str) and field_profile and 'type' in field_profile:
            field_type = field_profile['type']
            if field_type in Profile['types']:
                # This is an enum field - convert string to number
                for num_val, str_val in Profile['types'][field_type].items():
                    if str_val == field_value:
                        field_value = int(num_val)
                        break
                else:
                    # Unknown enum value - use invalid
                    field_value = 0  # Default to 0 for unknown enum values
        
        if 'type' in field_profile and field_profile['type'] in FIT.FIELD_TYPE_TO_BASE_TYPE:
            base_type = FIT.FIELD_TYPE_TO_BASE_TYPE[field_profile['type']]
            base_type_def = FIT.BASE_TYPE_DEFINITIONS[base_type]
            
            # Special handling for string types
            if field_profile['type'] == 'string':
                if isinstance(field_value, str):
                    size = len(field_value) + 1  # Include null terminator
                else:
                    size = 1  # Fallback for empty/null strings
                return base_type, size
            
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
                string_base_type = FIT.BASE_TYPE['STRING']
                string_size = min(len(field_value) + 1, 255)
                return string_base_type, string_size
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
            elif isinstance(field_value, datetime.datetime):
                # Datetime objects should be encoded as uint32 timestamps
                return FIT.BASE_TYPE['UINT32'], 4
            else:
                return FIT.BASE_TYPE['UINT8'], 1

    def _get_global_message_number(self, msg_type: str) -> int:
        '''Get the global message number for a message type'''
        for global_num, msg_info in Profile['messages'].items():
            if msg_info.get('messages_key') == msg_type:
                return global_num
        return None