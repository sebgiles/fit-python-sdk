#!/usr/bin/env python3
"""Check the difference in left_power_phase"""

val1 = 345.9375054052735
val2 = 344.53125538330085

diff = abs(val1 - val2)
rel_diff = diff / val2

print(f"val1: {val1}")
print(f"val2: {val2}")
print(f"absolute difference: {diff}")
print(f"relative difference: {rel_diff:.10f}")
print(f"relative diff as percentage: {rel_diff * 100:.6f}%")

# Check what tolerance we'd need
rtol_needed = diff / abs(val2)
print(f"rtol needed: {rtol_needed:.10f}")