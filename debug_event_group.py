#!/usr/bin/env python3
"""Debug event_group field specifically"""

from garmin_fit_sdk import Decoder, Stream, Encoder
import tempfile
import os

def debug_event_group():
    print("=== DEBUGGING EVENT_GROUP FIELD ===")
    
    # Look at files that have event_group
    files_with_events = [
        "tests/fits/HrmPluginTestActivity.fit",
        "tests/fits/WithGearChangeData.fit"
    ]
    
    for filepath in files_with_events:
        print(f"\n=== {os.path.basename(filepath)} ===")
        
        # Decode original
        stream = Stream.from_file(filepath)
        decoder = Decoder(stream)
        messages, _ = decoder.read()
        
        # Find messages with event_group
        event_messages = []
        for msg_type, msg_list in messages.items():
            for i, msg in enumerate(msg_list):
                if 'event_group' in msg:
                    event_messages.append({
                        'type': msg_type,
                        'index': i,
                        'event_group': msg['event_group'],
                        'full_msg': msg
                    })
        
        print(f"Found {len(event_messages)} messages with event_group:")
        for event in event_messages:
            print(f"  {event['type']}[{event['index']}]: event_group={event['event_group']}")
            # Show other event-related fields
            event_fields = {k: v for k, v in event['full_msg'].items() if 'event' in k.lower()}
            print(f"    Event fields: {event_fields}")
        
        # Test encoding just the event messages
        if event_messages:
            # Create test with just event messages
            test_messages = {}
            for event in event_messages:
                msg_type = event['type']
                if msg_type not in test_messages:
                    test_messages[msg_type] = []
                test_messages[msg_type].append(event['full_msg'])
            
            print(f"\nTesting encoding of {len(event_messages)} event messages...")
            encoder = Encoder(test_messages)
            
            with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            try:
                result = encoder.write_to_file(temp_path)
                print(f"Encoding result: {result}")
                
                if result:
                    # Decode back
                    new_stream = Stream.from_file(temp_path)
                    new_decoder = Decoder(new_stream)
                    new_messages, errors = new_decoder.read()
                    
                    print(f"Decoding errors: {len(errors)}")
                    if errors:
                        for error in errors:
                            print(f"  Error: {error}")
                    
                    # Count event_group fields in result
                    new_event_count = 0
                    for msg_type, msg_list in new_messages.items():
                        for msg in msg_list:
                            if 'event_group' in msg:
                                new_event_count += 1
                                print(f"  Decoded: {msg_type} event_group={msg['event_group']}")
                    
                    print(f"Event_group count: {len(event_messages)} -> {new_event_count}")
                    
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

if __name__ == '__main__':
    debug_event_group()