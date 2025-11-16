#!/usr/bin/env python3
"""Test precise scaling and rounding"""

def test_precise_scaling():
    print("=== TESTING PRECISE SCALING ===")
    
    # The exact values from our test
    original = [9.843750153808596, 203.9062531860352]
    scale = 0.7111111
    
    print(f"Original values: {original}")
    print(f"Scale factor: {scale}")
    
    # Test more precise scale
    precise_scale = 64.0 / 90.0  # 0.7111111111111111...
    print(f"Precise scale (64/90): {precise_scale}")
    
    # Test with different rounding
    for desc, rounder in [("int()", int), ("round()", round)]:
        print(f"\nUsing {desc} for encoding:")
        
        # Encode with precise scale
        encoded = [rounder(v / precise_scale) for v in original]
        print(f"  Encoded: {encoded}")
        
        # Decode back
        decoded = [e * precise_scale for e in encoded]
        print(f"  Decoded: {decoded}")
        print(f"  Difference: {[abs(o - d) for o, d in zip(original, decoded)]}")
        
        # Try with original scale
        encoded_orig = [rounder(v / scale) for v in original]
        print(f"  With orig scale - Encoded: {encoded_orig}")
        decoded_orig = [e * scale for e in encoded_orig]
        print(f"  With orig scale - Decoded: {decoded_orig}")
        print(f"  With orig scale - Difference: {[abs(o - d) for o, d in zip(original, decoded_orig)]}")

if __name__ == '__main__':
    test_precise_scaling()