'''encoder.py: Contains the encoder class which is used to encode fit files.'''

###########################################################################################
# Copyright 2025 Garmin International, Inc.
# Licensed under the Flexible and Interoperable Data Transfer (FIT) Protocol License; you
# may not use this file except in compliance with the Flexible and Interoperable Data
# Transfer (FIT) Protocol License.
###########################################################################################


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

    def write_to_file(self, filename: str) -> bool:
        '''
        Writes the messages to a FIT file.
        
        Args:
            filename: The path where the FIT file should be written
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            NotImplementedError: This method is not yet implemented
        '''
        raise NotImplementedError("Encoder.write_to_file() is not yet implemented")

    def write_to_bytes(self) -> bytearray:
        '''
        Writes the messages to a bytearray in FIT format.
        
        Returns:
            bytearray: The encoded FIT data
            
        Raises:
            NotImplementedError: This method is not yet implemented
        '''
        raise NotImplementedError("Encoder.write_to_bytes() is not yet implemented")