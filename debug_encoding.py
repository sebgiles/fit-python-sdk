#!/usr/bin/env python3

import sys
import tempfile
from garmin_fit_sdk.stream import Stream
from garmin_fit_sdk.decoder import Decoder
from garmin_fit_sdk.encoder import Encoder

def debug_encoded_fields():
    fit_file = "tests/fits/WithGearChangeData.fit"
    
    # Decode the original file
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    stream.reset()
    messages, errors = decoder.read()
    
    # Get record 25
    record = messages['record_mesgs'][25]
    print(f"Original record[25] fields: {list(record.keys())}")
    
    # Encode to temp file
    encoder = Encoder(messages)
    
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    result = encoder.write_to_file(temp_path)
    print(f"Encoding result: {result}")
    
    # Decode the encoded file
    new_stream = Stream.from_file(temp_path)
    new_decoder = Decoder(new_stream)
    new_stream.reset()
    new_messages, new_errors = new_decoder.read()
    
    # Get the re-decoded record 25
    new_record = new_messages['record_mesgs'][25]
    print(f"Re-decoded record[25] fields: {list(new_record.keys())}")
    
    # Show missing fields
    orig_fields = set(k for k in record.keys() if not isinstance(k, int))
    new_fields = set(k for k in new_record.keys() if not isinstance(k, int))
    
    missing_fields = orig_fields - new_fields
    extra_fields = new_fields - orig_fields
    
    print(f"\nMissing fields: {missing_fields}")
    print(f"Extra fields: {extra_fields}")
    
    # Check specific values
    for field in ['cadence', 'fractional_cadence', 'left_pco', 'right_pco']:
        if field in record and field in new_record:
            print(f"{field}: {record[field]} -> {new_record[field]}")
        elif field in record:
            print(f"{field}: {record[field]} -> MISSING")
        elif field in new_record:
            print(f"{field}: NEW -> {new_record[field]}")

if __name__ == "__main__":
    debug_encoded_fields()