#!/usr/bin/env python3
"""Work backwards from decoded values to find what raw values should be"""

def reverse_engineer_scaling():
    print("=== REVERSE ENGINEERING SCALING ===")
    
    # Known decoded values
    decoded_values = [9.843750153808596, 203.9062531860352]
    scale = 0.7111111
    offset = 0
    
    print(f"Decoded values: {decoded_values}")
    print(f"Scale: {scale}, Offset: {offset}")
    
    # Try different decoder formulas to see what raw values would work
    decoder_formulas = [
        ("actual = raw * scale + offset", lambda raw: raw * scale + offset),
        ("actual = raw * scale - offset", lambda raw: raw * scale - offset), 
        ("actual = raw / scale + offset", lambda raw: raw / scale + offset),
        ("actual = raw / scale - offset", lambda raw: raw / scale - offset),
        ("actual = (raw + offset) * scale", lambda raw: (raw + offset) * scale),
        ("actual = (raw - offset) * scale", lambda raw: (raw - offset) * scale),
        ("actual = (raw + offset) / scale", lambda raw: (raw + offset) / scale),
        ("actual = (raw - offset) / scale", lambda raw: (raw - offset) / scale),
    ]
    
    for desc, decoder_func in decoder_formulas:
        print(f"\nTesting decoder: {desc}")
        
        # For each decoded value, find what raw value would produce it
        for decoded in decoded_values:
            # Try raw values from 0 to 300 
            best_raw = None
            best_diff = float('inf')
            
            for raw in range(301):
                calculated = decoder_func(raw)
                diff = abs(calculated - decoded)
                if diff < best_diff:
                    best_diff = diff
                    best_raw = raw
            
            print(f"  Decoded {decoded:.6f} -> Raw {best_raw} (diff: {best_diff:.8f})")
            
            # Verify
            if best_raw is not None:
                verify = decoder_func(best_raw)
                print(f"    Verify: raw {best_raw} -> {verify:.6f}")

if __name__ == '__main__':
    reverse_engineer_scaling()