#!/usr/bin/env python3
'''
FIT File Processing Script

This script takes a FIT file path as an argument and performs:
1. Decode the original FIT file into a message data structure
2. Modify the data structure (modification logic to be implemented)
3. Encode the modified data structure to a new FIT file

Usage:
    python3 process_fit_file.py <input_file.fit> [output_file.fit]
'''

import sys
import os
from pathlib import Path

from garmin_fit_sdk import Decoder, Encoder, Stream


def decode_fit_file(input_path):
    """
    Decode a FIT file into a message data structure.
    
    Args:
        input_path (str): Path to the input FIT file
        
    Returns:
        tuple: (messages_dict, success_bool)
    """
    print(f"📖 Decoding FIT file: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"❌ Input file does not exist: {input_path}")
        return None, False
    
    try:
        # Create stream and decoder
        stream = Stream.from_file(input_path)
        decoder = Decoder(stream)
        
        # Validate file format
        stream.reset()
        if not decoder.is_fit():
            print("❌ File is not a valid FIT file")
            return None, False
        print("✓ Valid FIT file format")
        
        # Check integrity
        stream.reset()
        if not decoder.check_integrity():
            print("❌ File failed integrity check")
            return None, False
        print("✓ File passed integrity check")
        
        # Decode messages
        stream.reset()
        messages, errors = decoder.read()
        
        if errors:
            print(f"❌ Decoding errors: {errors}")
            return None, False
        
        # Show summary
        total_messages = sum(len(msgs) for msgs in messages.values())
        print(f"✓ Successfully decoded {len(messages)} message types ({total_messages} total messages)")
        
        for msg_type, msgs in messages.items():
            print(f"  - {msg_type}: {len(msgs)} messages")
            
        return messages, True
        
    except Exception as e:
        print(f"❌ Error decoding file: {e}")
        return None, False


def modify_messages(messages):
    """
    Modify the message data structure.
    Implement your custom modification logic here.
    
    Args:
        messages (dict): The decoded messages dictionary
        
    Returns:
        dict: The modified messages dictionary
    """
    print("\n🔧 Message modification point")
    print("   (Implement your custom modification logic here)")
    
    # TODO: Add your modification logic here
    # Examples:
    # 
    # # Modify specific field values
    # if 'record_mesgs' in messages:
    #     for record in messages['record_mesgs']:
    #         if 'speed' in record:
    #             record['speed'] = record['speed'] * 1.1  # Increase speed by 10%
    #
    # # Add custom fields
    # if 'file_id_mesgs' in messages and len(messages['file_id_mesgs']) > 0:
    #     messages['file_id_mesgs'][0]['custom_field'] = 'processed'
    #
    # # Filter messages
    # if 'event_mesgs' in messages:
    #     # Keep only certain types of events
    #     messages['event_mesgs'] = [msg for msg in messages['event_mesgs'] 
    #                               if msg.get('event_type') == 'start']
    
    print("✓ No modifications applied (implement modification logic above)")
    return messages


def encode_fit_file(messages, output_path):
    """
    Encode a message data structure into a new FIT file.
    
    Args:
        messages (dict): The message data structure to encode
        output_path (str): Path where the new FIT file should be written
        
    Returns:
        bool: True if encoding was successful
    """
    print(f"\n� Encoding to new FIT file: {output_path}")
    
    try:
        # Create encoder
        encoder = Encoder(messages)
        print("✓ Encoder created successfully")
        
        # Encode to file
        result = encoder.write_to_file(output_path)
        
        if result and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✓ Encoding completed successfully")
            print(f"✓ Output file size: {file_size} bytes")
            return True
        else:
            print("❌ Encoding failed - no output file created")
            return False
            
    except Exception as e:
        print(f"❌ Encoding error: {e}")
        return False


def main():
    """Main function to handle command line arguments and orchestrate the processing"""
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 process_fit_file.py <input_file.fit> [output_file.fit]")
        print("\nExample:")
        print("  python3 process_fit_file.py tests/fits/ActivityDevFields.fit output.fit")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"processed_{os.path.basename(input_file)}"
    
    print("🚀 FIT File Processing")
    print("=" * 30)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    
    # Step 1: Decode original file
    messages, success = decode_fit_file(input_file)
    if not success:
        sys.exit(1)
    
    # Step 2: Modify messages
    messages = modify_messages(messages)
    
    # Step 3: Encode to new file
    if not encode_fit_file(messages, output_file):
        sys.exit(1)
    
    print("\n" + "=" * 30)
    print("✅ Processing completed successfully!")
    print(f"📁 Processed FIT file created: {output_file}")


if __name__ == "__main__":
    main()
