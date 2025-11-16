import pytest
import os
from io import BytesIO
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.encoder import Encoder


class TestScalingIssues:
    
    def test_software_version_scaling_issue(self):
        """Test to investigate software_version scaling issue: 1.0 vs 0.01"""
        
        # Step 1: Decode ActivityDevFields.fit to get original software_version
        original_stream = Stream.from_file('tests/fits/ActivityDevFields.fit')
        original_decoder = Decoder(original_stream)
        original_stream.reset()
        original_messages, original_errors = original_decoder.read()
        
        assert len(original_errors) == 0
        assert 'device_info_mesgs' in original_messages
        
        device_info = original_messages['device_info_mesgs'][0]
        original_software_version = device_info.get('software_version')
        print(f"Original software_version: {original_software_version} (type: {type(original_software_version)})")
        
        # Step 2: Create a simple test message with the same software_version
        test_messages = {
            'device_info_mesgs': [{
                'manufacturer': 'development',
                'product': 0,
                'software_version': original_software_version,
                'serial_number': 12345
            }]
        }
        
        # Step 3: Encode and decode
        encoder = Encoder(test_messages)
        encoded_bytes = encoder.write_to_bytes()
        
        bytes_io = BytesIO(encoded_bytes)
        stream = Stream.from_bytes_io(bytes_io)
        decoder = Decoder(stream)
        decoded_messages, errors = decoder.read()
        
        assert len(errors) == 0
        assert 'device_info_mesgs' in decoded_messages
        
        decoded_software_version = decoded_messages['device_info_mesgs'][0].get('software_version')
        print(f"Decoded software_version: {decoded_software_version} (type: {type(decoded_software_version)})")
        
        # Step 4: Compare values
        print(f"Original: {original_software_version}")
        print(f"Decoded:  {decoded_software_version}")
        print(f"Equal? {original_software_version == decoded_software_version}")
        
        # This test documents the current behavior - we expect it to fail initially
        assert original_software_version == decoded_software_version, \
            f"software_version changed from {original_software_version} to {decoded_software_version}"
    
    def test_software_version_profile_inspection(self):
        """Inspect the profile definition for software_version field"""
        from garmin_fit_sdk.profile import Profile
        
        # Find device_info message profile
        device_info_profile = None
        for msg_num, msg_profile in Profile['messages'].items():
            if msg_profile.get('name') == 'device_info':
                device_info_profile = msg_profile
                break
        
        assert device_info_profile is not None, "device_info message profile not found"
        
        # Find software_version field
        software_version_field = None
        for field_num, field_profile in device_info_profile['fields'].items():
            if field_profile.get('name') == 'software_version':
                software_version_field = field_profile
                break
        
        assert software_version_field is not None, "software_version field not found"
        
        print(f"software_version field profile: {software_version_field}")
        
        # Key things to check:
        # - type: should be uint16
        # - scale: should be [100] 
        # - This means raw value * scale = actual value
        # - So raw value 100 * scale 100 = 10000 (but we want 1.0)
        # - This suggests: actual_value = raw_value / scale
        
        assert 'scale' in software_version_field, "software_version should have scale"
        assert software_version_field['scale'] == [100], f"Expected scale [100], got {software_version_field['scale']}"
        
        print(f"Scale factor: {software_version_field['scale'][0]}")
    
    def test_scale_factor_calculation_logic(self):
        """Test how scale factors should be applied during encoding"""
        
        # If software_version has scale [100] and we want to store 1.0:
        # - During encoding: raw_value = actual_value * scale = 1.0 * 100 = 100
        # - During decoding: actual_value = raw_value / scale = 100 / 100 = 1.0
        
        # But if we're seeing 1.0 -> 0.01, it suggests:
        # - During encoding: raw_value = actual_value / scale = 1.0 / 100 = 0.01 (WRONG)
        # - During decoding: actual_value = raw_value * scale = 0.01 * 100 = 1.0 (WRONG)
        
        # Or the other way:
        # - During encoding: raw_value = actual_value (no scaling) = 1.0
        # - During decoding: actual_value = raw_value / scale = 1.0 / 100 = 0.01 (WRONG)
        
        actual_value = 1.0
        scale_factor = 100
        
        # Correct encoding: multiply by scale to get integer raw value
        raw_value_correct = actual_value * scale_factor
        print(f"Correct encoding: {actual_value} * {scale_factor} = {raw_value_correct}")
        
        # Correct decoding: divide by scale to get actual value
        decoded_value_correct = raw_value_correct / scale_factor
        print(f"Correct decoding: {raw_value_correct} / {scale_factor} = {decoded_value_correct}")
        
        assert decoded_value_correct == actual_value, "Scale calculation logic should preserve original value"
        
        # Test the broken behavior we're seeing
        broken_encoded = actual_value  # No scaling during encode
        broken_decoded = broken_encoded / scale_factor  # Only scaling during decode
        print(f"Broken behavior: {actual_value} -> {broken_encoded} -> {broken_decoded}")
        
        assert broken_decoded == 0.01, f"Expected broken behavior to produce 0.01, got {broken_decoded}"