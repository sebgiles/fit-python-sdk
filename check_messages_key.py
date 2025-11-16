#!/usr/bin/env python3
"""Check messages_key field in profile"""

from garmin_fit_sdk import Profile

def check_messages_key():
    print("=== CHECKING messages_key FIELD ===")
    
    # Look at message 20 (record) specifically
    if 20 in Profile['messages']:
        record_profile = Profile['messages'][20]
        print(f"Record message (20) profile keys: {record_profile.keys()}")
        messages_key = record_profile.get('messages_key')
        print(f"messages_key: {messages_key}")
        
        # Check a few other message types
        for msg_id in [0, 18, 19, 20, 21]:
            if msg_id in Profile['messages']:
                msg_profile = Profile['messages'][msg_id]
                messages_key = msg_profile.get('messages_key', 'NOT_FOUND')
                print(f"Message {msg_id}: messages_key = {messages_key}")
            else:
                print(f"Message {msg_id}: NOT FOUND")
    
    print(f"\nLooking for messages_key = 'record_mesgs':")
    found = False
    for msg_id, msg_profile in Profile['messages'].items():
        if msg_profile.get('messages_key') == 'record_mesgs':
            print(f"Found! Message {msg_id} has messages_key = 'record_mesgs'")
            found = True
    
    if not found:
        print("No message found with messages_key = 'record_mesgs'!")

if __name__ == '__main__':
    check_messages_key()