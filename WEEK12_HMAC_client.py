import socket
import hmac
import hashlib

def start_client():
    print("--- HMAC Message Sender ---")
    # Ask for the client's secret key (Allows you to do Test 3)
    secret_key = input("Enter the client's shared secret key: ").encode('utf-8')

    # Accept the original message from the user
    original_msg = input("Enter the message to send: ")

    # Generate the HMAC-SHA256 based on the original message and key
    generated_mac = hmac.new(secret_key, original_msg.encode('utf-8'), hashlib.sha256).hexdigest()
    
    print(f"\nGenerated HMAC: {generated_mac}")

    # --- TESTING HOOK: Allows you to perform Test 2 manually ---
    print("\n[Testing Options]")
    tamper = input("Do you want to act as an attacker and modify the message before sending? (y/n): ")
    
    if tamper.lower() == 'y':
        msg_to_send = input("Enter the fake/altered message: ")
        print("Sending altered message with original HMAC...")
    else:
        msg_to_send = original_msg
        print("Sending original message and HMAC...")

    # Connect to the server and send the data
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 65432))
        
        # Package the message and HMAC together using '|||' as a separator
        payload = f"{msg_to_send}|||{generated_mac}"
        client_socket.send(payload.encode('utf-8'))
        
        print("\nTransmission sent successfully!")
        client_socket.close()
    except ConnectionRefusedError:
        print("\nError: Could not connect to the server. Make sure hmac_server.py is running first!")

if __name__ == "__main__":
    start_client()