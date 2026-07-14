import hashlib

#  STEP 1: Accept a message from the user 
message = input("Enter a message to hash: ")
msg_bytes = message.encode('utf-8')
block_size = 8

print("\n Original Message Length:", len(msg_bytes), "bytes")

#  STEP 2: Pad the message 
pad_len = block_size - (len(msg_bytes) % block_size)
padded_msg = msg_bytes + bytes([pad_len] * pad_len)

print("\n Padding Applied")
print("Added", pad_len, "bytes of padding.")
print("Padded message (in hex):", padded_msg.hex())
print("New message length:", len(padded_msg), "bytes")

# STEP 3: Split into fixed-size blocks 
blocks = []
for i in range(0, len(padded_msg), block_size):
    block = padded_msg[i:i + block_size]
    blocks.append(block)

print("\n Splitting into Blocks")
for i in range(len(blocks)):
    print(f"Block {i+1}: {blocks[i].hex()}")

#  STEP 4: Use an Initial Value (IV) 
current_state = b'INIT_IV!'

print("\n Initial Value (IV) Loaded")
print("IV (in hex):", current_state.hex())

print("\n Iteratively Combining and Hashing")
#  STEP 5: Iteratively combine IV with each block and hash 
for i in range(len(blocks)):
    # Combine the current state with the current block
    combined_data = current_state + blocks[i]
    
    # Hash the combined data using SHA-256
    full_hash = hashlib.sha256(combined_data).digest()
    
    print(f"--- Processing Block {i+1} ---")
    print("Combined State + Block:", combined_data.hex())
    
    # Update the state (taking the first 8 bytes of the hash)
    current_state = full_hash[:8]
    print("New State for next round:", current_state.hex())

#  STEP 6: Display the final digest 
final_digest = hashlib.sha256(current_state).hexdigest()

print("\n[STEP 6] Final Digest")
print(final_digest)
print("----------------------------------------\n")