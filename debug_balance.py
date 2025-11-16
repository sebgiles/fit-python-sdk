#!/usr/bin/env python3
"""Debug left_right_balance field count issues"""

from garmin_fit_sdk import Decoder, Stream, Encoder
import tempfile

def debug_left_right_balance():
    print("=== DEBUGGING LEFT_RIGHT_BALANCE COUNT ISSUE ===")
    
    # Focus on WithGearChangeData.fit since it has this field
    stream = Stream.from_file("tests/fits/WithGearChangeData.fit")
    decoder = Decoder(stream)
    messages, _ = decoder.read()
    
    # Find messages with left_right_balance
    balance_messages = []
    for msg_type, msg_list in messages.items():
        for i, msg in enumerate(msg_list):
            if 'left_right_balance' in msg:
                balance_messages.append({
                    'type': msg_type,
                    'index': i,
                    'balance': msg['left_right_balance'],
                    'fields': set(msg.keys())
                })
    
    print(f"Found {len(balance_messages)} messages with left_right_balance")
    
    # Group by field pattern to see if some have different patterns
    field_patterns = {}
    for msg in balance_messages:
        pattern = frozenset(msg['fields'])
        if pattern not in field_patterns:
            field_patterns[pattern] = []
        field_patterns[pattern].append(msg)
    
    print(f"Field patterns: {len(field_patterns)}")
    for i, (pattern, msgs) in enumerate(field_patterns.items()):
        print(f"  Pattern {i+1}: {len(msgs)} messages")
        # Separate string and int field names for display
        str_fields = [f for f in pattern if isinstance(f, str)]
        int_fields = [f for f in pattern if isinstance(f, int)]
        print(f"    String fields: {sorted(str_fields)[:8]}...")
        if int_fields:
            print(f"    Integer fields: {sorted(int_fields)[:8]}...")
        if 'left_right_balance' in pattern:
            sample_balance = msgs[0]['balance']
            print(f"    Sample balance: {sample_balance}")
    
    # Test full encoding to see message counts
    print(f"\nTesting full encoding...")
    encoder = Encoder(messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    result = encoder.write_to_file(temp_path)
    
    if result:
        new_stream = Stream.from_file(temp_path)
        new_decoder = Decoder(new_stream)
        new_messages, errors = new_decoder.read()
        
        # Count new left_right_balance messages
        new_balance_count = 0
        for msg_type, msg_list in new_messages.items():
            for msg in msg_list:
                if 'left_right_balance' in msg:
                    new_balance_count += 1
        
        print(f"Balance count: {len(balance_messages)} -> {new_balance_count}")
        print(f"Missing: {len(balance_messages) - new_balance_count} messages")
        
        # Check if it's specific message types or patterns
        print(f"Checking which messages are missing...")
        
        # Compare by message type
        for msg_type in set(msg['type'] for msg in balance_messages):
            orig_count = len([m for m in balance_messages if m['type'] == msg_type])
            new_count = 0
            for msg in new_messages.get(msg_type, []):
                if 'left_right_balance' in msg:
                    new_count += 1
            if orig_count != new_count:
                print(f"  {msg_type}: {orig_count} -> {new_count}")

if __name__ == '__main__':
    debug_left_right_balance()