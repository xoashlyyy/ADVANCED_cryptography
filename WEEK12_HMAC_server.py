import socket
import hmac
import hashlib

def start_server():
    print("--- HMAC Verification Server ---")
    # Ask for the server's secret key (Allows you to do Test 3)
    secret_key = input("Enter the server's shared secret key: ").encode('utf-8')

    # Set up the network socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 65432))
    server_socket.listen(1)
    
    print("\nServer is running and listening on port 65432...")

    while True:
        # Wait for a client to connect
        conn, addr = server_socket.accept()
        data = conn.recv(1024).decode('utf-8')
        
        if not data:
            break

        print("\n" + "="*40)
        print("Incoming Transmission Detected!")
        
        # Split the received data into the message and the HMAC
        # We use '|||' as a simple separator between the two
        try:
            received_msg, received_mac = data.split('|||')
        except ValueError:
            print("Error: Received malformed data.")
            conn.close()
            continue

        print(f"1. Received Message: '{received_msg}'")
        print(f"2. Received HMAC:    {received_mac}")

        # Recompute the HMAC using the server's secret key and the received message
        expected_mac = hmac.new(secret_key, received_msg.encode('utf-8'), hashlib.sha256).hexdigest()
        print(f"3. Computed HMAC:    {expected_mac}")

        # Verify if they match
        print("\n--- Verification Result ---")
        if hmac.compare_digest(received_mac, expected_mac):
            print("[+] Integrity Verified")
        else:
            print("[-] Message Modified!")
        
        print("="*40)
        conn.close()

if __name__ == "__main__":
    start_server()