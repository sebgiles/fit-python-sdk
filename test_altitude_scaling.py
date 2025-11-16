#!/usr/bin/env python3
"""Debug altitude scaling specifically"""

def test_altitude_scaling():
    print("=== TESTING ALTITUDE SCALING ===")
    
    # Altitude field profile
    scale = 5
    offset = 500
    
    # Test values from the failed test
    test_cases = [11980.2, 28.8]
    
    print(f"Scale: {scale}, Offset: {offset}")
    
    for actual in test_cases:
        print(f"\nActual altitude: {actual}")
        
        # Test different formulas
        formulas = [
            ("raw = (actual - offset) * scale", lambda v: round((v - offset) * scale)),
            ("raw = (actual + offset) * scale", lambda v: round((v + offset) * scale)),
            ("raw = (actual - offset) / scale", lambda v: round((v - offset) / scale)),
            ("raw = (actual + offset) / scale", lambda v: round((v + offset) / scale)),
        ]
        
        for desc, encoder_func in formulas:
            raw = encoder_func(actual)
            print(f"  {desc}")
            print(f"    Raw: {raw}")
            
            # Test different decoder formulas
            decoder_results = [
                ("decoded = raw * scale + offset", raw * scale + offset),
                ("decoded = raw * scale - offset", raw * scale - offset),
                ("decoded = raw / scale + offset", raw / scale + offset),
                ("decoded = raw / scale - offset", raw / scale - offset),
            ]
            
            for dec_desc, decoded in decoder_results:
                diff = abs(decoded - actual)
                if diff < 0.1:
                    print(f"    ✅ {dec_desc}: {decoded} (diff: {diff})")
                else:
                    print(f"    ❌ {dec_desc}: {decoded} (diff: {diff})")

if __name__ == '__main__':
    test_altitude_scaling()