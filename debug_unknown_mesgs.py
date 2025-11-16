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
    
    # Organize by message type
    by_type = {}
    for msg in messages:
        msg_type = msg.name
        if msg_type not in by_type:
            by_type[msg_type] = []
        by_type[msg_type].append(msg)
    
    # Print all message types
    print("All message types in original:")
    for msg_type in sorted(by_type.keys()):
        count = len(by_type[msg_type])
        # Check if it's a numbered (unknown) type
        is_numbered = msg_type.isdigit()
        if is_numbered:
            print(f"  ❌ {msg_type}: {count} messages (UNKNOWN/NUMBERED)")
            # Print first message details
            first_msg = by_type[msg_type][0]
            print(f"     Type: {first_msg.type}, Fields: {list(first_msg.get_fields().keys())}")
        else:
            print(f"  ✅ {msg_type}: {count} messages")
    
    # Test encoding just the unknown messages
    print("\n=== Testing encoder handling of unknown messages ===")
    
    numbered_messages = []
    for msg_type, msgs in by_type.items():
        if msg_type.isdigit():
            numbered_messages.extend(msgs)
    
    print(f"Found {len(numbered_messages)} unknown/numbered messages")
    
    # Try encoding them
    encoder = Encoder(numbered_messages)
    
    # Try to encode just these unknown messages
    try:
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp:
            temp_file = tmp.name
        
        success = encoder.write_to_file(temp_file)
        print(f"\n✅ Encoder returned: {success}")
        
        if os.path.exists(temp_file):
            file_size = os.path.getsize(temp_file)
            print(f"✅ Created file: {file_size} bytes")
        
            # Try to decode them back
            stream2 = Stream.from_file(temp_file)
            decoder2 = Decoder(stream2)
            roundtrip_messages, roundtrip_errors = decoder2.read()
        
        print(f"Roundtrip: {len(roundtrip_messages)} messages, {len(roundtrip_errors)} errors")
        
        # Check what message types we got back
        roundtrip_by_type = {}
        for msg in roundtrip_messages:
            msg_type = msg.name
            if msg_type not in roundtrip_by_type:
                roundtrip_by_type[msg_type] = []
            roundtrip_by_type[msg_type].append(msg)
        
        print("Roundtrip message types:")
        for msg_type in sorted(roundtrip_by_type.keys()):
            count = len(roundtrip_by_type[msg_type])
            print(f"  {msg_type}: {count} messages")
        
        # Cleanup
        os.unlink(temp_file)
            
    except Exception as e:
        print(f"\n❌ Encoding failed: {e}")

if __name__ == "__main__":
    debug_unknown_messages()