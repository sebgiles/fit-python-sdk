import pytest
from garmin_fit_sdk.fit import BASE_TYPE, FIELD_TYPE_TO_BASE_TYPE, BASE_TYPE_DEFINITIONS
from garmin_fit_sdk.profile import Profile


class TestEnumTypeMapping:
    
    def test_event_type_mapping(self):
        """Test how event_type is mapped in the field type system"""
        
        print(f"FIELD_TYPE_TO_BASE_TYPE keys (first 20): {list(FIELD_TYPE_TO_BASE_TYPE.keys())[:20]}")
        
        if 'event_type' in FIELD_TYPE_TO_BASE_TYPE:
            base_type = FIELD_TYPE_TO_BASE_TYPE['event_type']
            print(f"event_type -> base_type: {base_type}")
            print(f"base_type definition: {BASE_TYPE_DEFINITIONS[base_type]}")
        else:
            print("event_type NOT found in FIELD_TYPE_TO_BASE_TYPE")
        
        # Check if event_type is in Profile types (enum values)
        if 'event_type' in Profile['types']:
            print(f"event_type enum values: {Profile['types']['event_type']}")
            if 'stop_all' in Profile['types']['event_type'].values():
                for num, name in Profile['types']['event_type'].items():
                    if name == 'stop_all':
                        print(f"'stop_all' -> enum value: {num}")
                        break
        else:
            print("event_type NOT found in Profile types")
    
    def test_string_vs_enum_logic(self):
        """Test the logic for determining when to treat a field as string vs enum"""
        
        # The key insight: if field_profile['type'] is 'string', treat as string
        # But if field_profile['type'] is 'event_type', treat as enum
        
        # Case 1: string type
        string_profile = {'type': 'string', 'name': 'product_name'}
        string_value = 'Test Product'
        
        print(f"String case:")
        print(f"  Profile type: {string_profile['type']}")
        print(f"  Value: {string_value}")
        print(f"  Should be: STRING base type")
        
        # Case 2: enum type  
        enum_profile = {'type': 'event_type', 'name': 'event_type'}
        enum_value = 'stop_all'
        
        print(f"\nEnum case:")
        print(f"  Profile type: {enum_profile['type']}")
        print(f"  Value: {enum_value}")
        print(f"  Should be: ENUM base type (uint8 or similar)")
        print(f"  Should convert 'stop_all' to numeric before determining type")