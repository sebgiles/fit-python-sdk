#!/usr/bin/env python3
"""Debug unknown/numbered message types that are getting lost"""

from garmin_fit_sdk import Decoder, Stream
from garmin_fit_sdk.encoder import Encoder

def debug_unknown_messages():
    fit_file = 'tests/fits/HrmPluginTestActivity.fit'
    
    print(f"=== Analyzing {fit_file} ===")
    
    # Decode original
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    messages, errors = decoder.read()
    
    print(f"Total message types: {len(messages)}")
    print(f"Message type keys: {list(messages.keys())}")
    
    # Check for numbered (unknown) message types
    numbered_types = []
    named_types = []
    
    for msg_type in messages.keys():
        if str(msg_type).isdigit():
            numbered_types.append(msg_type)
        else:
            named_types.append(msg_type)
    
    print(f"\n✅ Named message types ({len(named_types)}):")
    for msg_type in sorted(named_types):
        count = len(messages[msg_type])
        print(f"  {msg_type}: {count} messages")
    
    print(f"\n❌ Numbered/Unknown message types ({len(numbered_types)}):")
    for msg_type in sorted(numbered_types, key=lambda x: int(x)):
        count = len(messages[msg_type])
        print(f"  {msg_type}: {count} messages")
        # Show first message details
        if messages[msg_type]:
            first_msg = messages[msg_type][0]
            if hasattr(first_msg, 'type'):
                print(f"     Message type: {first_msg.type}")
            fields = first_msg.keys() if hasattr(first_msg, 'keys') else []
            print(f"     Fields: {list(fields)}")
    
    # Now test if our encoder handles these unknown types
    print(f"\n=== Testing encoder with unknown types ===")
    
    # The encoder expects a dictionary, not a flat list
    print(f"Total message types to encode: {len(messages)}")
    
    # Try encoding with the dictionary format (as the decoder returns it)
    encoder = Encoder(messages)
    
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp:
        temp_file = tmp.name
    
    try:
        success = encoder.write_to_file(temp_file)
        print(f"Encoder result: {success}")
        
        if os.path.exists(temp_file):
            file_size = os.path.getsize(temp_file)
            print(f"Created file: {file_size} bytes")
            
            # Decode back
            stream2 = Stream.from_file(temp_file)
            decoder2 = Decoder(stream2)
            roundtrip_messages, roundtrip_errors = decoder2.read()
            
            print(f"Roundtrip message types: {len(roundtrip_messages)}")
            print(f"Keys: {list(roundtrip_messages.keys())}")
            
            # Compare original vs roundtrip keys
            original_keys = set(messages.keys())
            roundtrip_keys = set(roundtrip_messages.keys())
            
            missing_keys = original_keys - roundtrip_keys
            extra_keys = roundtrip_keys - original_keys
            
            if missing_keys:
                print(f"\n❌ Missing message types: {missing_keys}")
            if extra_keys:
                print(f"\n🆕 Extra message types: {extra_keys}")
            if not missing_keys and not extra_keys:
                print(f"\n✅ All message types preserved!")
        
        # Cleanup
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"Encoding failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_unknown_messages()