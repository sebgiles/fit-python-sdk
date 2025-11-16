#!/usr/bin/env python3
"""Find what raw value produces -127 when decoded"""

def find_raw_for_invalid():
    print("=== FINDING RAW VALUE FOR -127 ===")
    
    target = -127.0
    scale = 5
    offset = 500
    
    print(f"Target decoded value: {target}")
    print(f"Scale: {scale}, Offset: {offset}")
    print(f"Decoder formula: actual = (raw / scale) + offset")
    
    # Calculate what raw value should produce -127
    # -127 = (raw / 5) + 500
    # raw = (-127 - 500) * 5
    calculated_raw = (target - offset) * scale
    print(f"Calculated raw for {target}: {calculated_raw}")
    
    # Test it
    verification = (calculated_raw / scale) + offset
    print(f"Verification: {calculated_raw} -> {verification}")
    
    # But since raw values are usually unsigned integers...
    # Maybe the invalid value is actually encoded differently
    
    # Let's try to see what raw values from 0-65535 produce values close to -127
    print(f"\nSearching for raw values that produce {target}:")
    candidates = []
    
    for raw in range(0, 65536):  # uint16 range
        decoded = (raw / scale) + offset
        if abs(decoded - target) < 0.1:
            candidates.append((raw, decoded))
    
    if candidates:
        print(f"Found candidates:")
        for raw, decoded in candidates:
            print(f"  Raw {raw} (0x{raw:04x}) -> {decoded}")
    else:
        print("No candidates found in uint16 range")
        
        # Check if there's a special invalid value
        uint16_invalid = 0xFFFF
        decoded_invalid = (uint16_invalid / scale) + offset
        print(f"UINT16 invalid (0x{uint16_invalid:04x}) decodes to: {decoded_invalid}")

if __name__ == '__main__':
    find_raw_for_invalid()