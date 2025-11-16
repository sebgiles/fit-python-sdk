#!/usr/bin/env python3
"""Test different scaling formulas to find the correct one"""

from garmin_fit_sdk import Decoder, Stream

def test_scaling_formulas():
    print("=== TESTING SCALING FORMULAS ===")
    
    # Get some real power phase data
    stream = Stream.from_file("tests/fits/WithGearChangeData.fit")
    decoder = Decoder(stream)
    messages, _ = decoder.read()
    
    # Find a message with power phase data
    sample_values = None
    for msg_type, msg_list in messages.items():
        for msg in msg_list:
            if 'left_power_phase' in msg and msg['left_power_phase'] is not None:
                sample_values = msg['left_power_phase']
                print(f"Found sample left_power_phase: {sample_values}")
                break
        if sample_values:
            break
    
    if sample_values:
        # Profile info for left_power_phase
        scale = 0.7111111
        offset = 0
        
        print(f"Scale: {scale}, Offset: {offset}")
        print(f"Sample decoded values: {sample_values}")
        
        # Test different encoding formulas
        formulas = [
            ("raw = (actual + offset) * scale", lambda v: int((v + offset) * scale)),
            ("raw = (actual + offset) / scale", lambda v: int((v + offset) / scale)),
            ("raw = actual * scale + offset", lambda v: int(v * scale + offset)),
            ("raw = actual / scale + offset", lambda v: int(v / scale + offset)),
            ("raw = (actual - offset) * scale", lambda v: int((v - offset) * scale)),
            ("raw = (actual - offset) / scale", lambda v: int((v - offset) / scale)),
        ]
        
        for desc, formula in formulas:
            print(f"\nTesting: {desc}")
            encoded_values = [formula(v) for v in sample_values]
            print(f"  Encoded: {encoded_values}")
            
            # Simulate decoding: actual = (raw * scale) - offset
            decoded_values = [(raw * scale) - offset for raw in encoded_values]
            print(f"  Decoded back: {decoded_values}")
            print(f"  Match original: {all(abs(orig - dec) < 0.01 for orig, dec in zip(sample_values, decoded_values))}")

if __name__ == '__main__':
    test_scaling_formulas()