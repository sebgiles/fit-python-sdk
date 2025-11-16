import pytest
from io import BytesIO
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.encoder import Encoder
import datetime


class TestAltitudeScaling:
    
    def test_altitude_scaling_issue(self):
        """Test altitude scaling with offset: 1028.8 vs 628.8"""
        
        # Create a simple test message with altitude
        test_messages = {
            'record_mesgs': [{
                'timestamp': datetime.datetime.now(datetime.timezone.utc),
                'altitude': 1028.8,
                'distance': 0.0
            }]
        }
        
        # Encode and decode
        encoder = Encoder(test_messages)
        encoded_bytes = encoder.write_to_bytes()
        
        bytes_io = BytesIO(encoded_bytes)
        stream = Stream.from_bytes_io(bytes_io)
        decoder = Decoder(stream)
        decoded_messages, errors = decoder.read()
        
        assert len(errors) == 0, f"Decoding errors: {errors}"
        assert 'record_mesgs' in decoded_messages
        
        decoded_altitude = decoded_messages['record_mesgs'][0]['altitude']
        print(f"Original altitude: {1028.8}")
        print(f"Decoded altitude:  {decoded_altitude}")
        print(f"Difference: {1028.8 - decoded_altitude}")
        
        # Altitude field profile: scale=[5], offset=[500]
        # Expected: raw = (1028.8 * 5) + 500 = 5644
        # Decode: actual = (5644 - 500) / 5 = 1028.8
        
        # Check if the scaling matches
        expected_raw = int((1028.8 * 5) + 500)
        print(f"Expected raw value: {expected_raw}")
        
        # This should preserve the altitude
        assert abs(decoded_altitude - 1028.8) < 0.1, f"Altitude should be preserved: {1028.8} vs {decoded_altitude}"