import random
import math
import hashlib
from datetime import datetime
import os
# TERMINAL COLORS FOR BONUS CREATIVE TASK

class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
# MATHEMATICAL HELPER FUNCTIONS

def miller_rabin(n, k=5):
    """Miller-Rabin primality test."""
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0: return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_large_prime(bits=512):
    """Generate a prime number of specified bit length."""
    while True:
        p = random.getrandbits(bits)
        # Ensure it's odd and has the correct bit length
        p |= (1 << bits - 1) | 1
        if miller_rabin(p):
            return p

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(e, phi):
    gcd, x, y = extended_gcd(e, phi)
    if gcd != 1:
        raise Exception('Modular inverse does not exist')
    return x % phi

def pollards_rho(n):
    """Pollard's Rho algorithm for integer factorization."""
    if n % 2 == 0: return 2
    x = random.randint(2, n - 1)
    y = x
    c = random.randint(1, n - 1)
    g = 1
    while g == 1:
        x = ((x * x) % n + c) % n
        y = ((y * y) % n + c) % n
        y = ((y * y) % n + c) % n
        g = math.gcd(abs(x - y), n)
        if g == n:
            return pollards_rho(n)
    return g
# RSA CORE FUNCTIONS

def generate_rsa_keys(bits=512):
    p = generate_large_prime(bits)
    q = generate_large_prime(bits)
    while p == q:
        q = generate_large_prime(bits)
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    e = 65537
    # Ensure e and phi are coprime
    while math.gcd(e, phi) != 1:
        e = random.randrange(3, phi - 1, 2)
        
    d = mod_inverse(e, phi)
    
    return (p, q, n, phi, (e, n), (d, n))

def encrypt_char_by_char(public_key, plaintext):
    e, n = public_key
    encrypted = [pow(ord(char), e, n) for char in plaintext]
    return encrypted

def decrypt_char_by_char(private_key, ciphertext):
    d, n = private_key
    decrypted_ascii = [pow(char, d, n) for char in ciphertext]
    original = ''.join(chr(char) for char in decrypted_ascii)
    return decrypted_ascii, original

def sign_message(private_key, message):
    d, n = private_key
    # Compute SHA-256 Hash
    hash_obj = hashlib.sha256(message.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    hash_int = int(hash_hex, 16)
    # Sign the hash
    signature = pow(hash_int, d, n)
    return hash_hex, signature

def verify_signature(public_key, message, signature):
    e, n = public_key
    # Compute original hash
    hash_obj = hashlib.sha256(message.encode('utf-8'))
    expected_hash_hex = hash_obj.hexdigest()
    
    # Recover hash from signature
    recovered_hash_int = pow(signature, e, n)
    recovered_hash_hex = hex(recovered_hash_int)[2:] # Remove '0x'
    
    # Pad with leading zeros in case they were lost during int conversion
    recovered_hash_hex = recovered_hash_hex.zfill(64)
    
    return expected_hash_hex, recovered_hash_hex, expected_hash_hex == recovered_hash_hex
# CREATIVE CHALLENGE: RSA SECURE CHAT

class ChatUser:
    def __init__(self, name, bits=512):
        self.name = name
        print(f"{Color.CYAN}[*] Generating keys for {self.name}...{Color.RESET}")
        _, _, _, _, self.public_key, self.private_key = generate_rsa_keys(bits)

def rsa_secure_chat():
    print(f"\n{Color.MAGENTA}================================={Color.RESET}")
    print(f"{Color.MAGENTA}      RSA SECURE CHAT ROOM       {Color.RESET}")
    print(f"{Color.MAGENTA}================================={Color.RESET}")
    print("Welcome to the Multi-User Secure Chat. Logs are saved to 'rsa_chat_log.txt'")
    
    alice = ChatUser("Alice")
    bob = ChatUser("Bob")
    
    filename = "rsa_chat_log.txt"
    with open(filename, "a") as f:
        f.write(f"\n--- New Chat Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
    
    while True:
        print(f"\n{Color.YELLOW}Who is sending a message? (A for Alice, B for Bob, Q to quit): {Color.RESET}", end="")
        choice = input().strip().upper()
        
        if choice == 'Q':
            break
        elif choice == 'A':
            sender, receiver = alice, bob
            color = Color.GREEN
        elif choice == 'B':
            sender, receiver = bob, alice
            color = Color.BLUE
        else:
            print(f"{Color.RED}Invalid choice.{Color.RESET}")
            continue
            
        message = input(f"{color}[{sender.name}] Enter message to {receiver.name}: {Color.RESET}")
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # 1. Encrypt
        ciphertext = encrypt_char_by_char(receiver.public_key, message)
        cipher_preview = str(ciphertext)[:50] + "..."
        
        # 2. Decrypt
        _, decrypted_msg = decrypt_char_by_char(receiver.private_key, ciphertext)
        
        # Output Trace
        print(f"   ↓ {Color.YELLOW}Encrypting with {receiver.name}'s Public Key...{Color.RESET}")
        print(f"   ↓ {Color.CYAN}Ciphertext: {cipher_preview}{Color.RESET}")
        print(f"   ↓ {Color.YELLOW}Sending over network...{Color.RESET}")
        print(f"   ↓ {Color.YELLOW}Decrypting with {receiver.name}'s Private Key...{Color.RESET}")
        print(f"[{timestamp}] {color}{receiver.name} successfully received: {decrypted_msg}{Color.RESET}")
        
        # Log to file
        with open(filename, "a") as f:
            f.write(f"[{timestamp}] {sender.name} -> {receiver.name} (Encrypted): {cipher_preview}\n")
            f.write(f"[{timestamp}] {sender.name} -> {receiver.name} (Decrypted): {decrypted_msg}\n")
# MAIN MENU SYSTEM

def main():
    pub_key, priv_key = None, None
    last_encrypted = None
    last_message = ""
    
    while True:

        print(f"{Color.CYAN}       RSA SECURITY SYSTEM       {Color.RESET}")
  
  
        print("1. Generate RSA Keys")
        print("2. Encrypt Message")
        print("3. Decrypt Message")
        print("4. Sign Message")
        print("5. Verify Signature")
        print("6. Miller-Rabin Prime Test")
        print("7. Pollard Rho Factorization (Small Prime Risk)")
        print(f"8. {Color.MAGENTA}RSA Secure Chat (Creative Task){Color.RESET}")
        print("9. Exit")
        
        choice = input("Enter choice: ")

        if choice == '1':
            print("\nGenerating 512-bit RSA Keys. Please wait...")
            p, q, n, phi, pub_key, priv_key = generate_rsa_keys(512)
            print(f"\n{Color.GREEN}Prime P:{Color.RESET} {str(p)[:30]}...")
            print(f"{Color.GREEN}Prime Q:{Color.RESET} {str(q)[:30]}...")
            print(f"{Color.GREEN}Modulus n:{Color.RESET} {str(n)[:30]}...")
            print(f"{Color.GREEN}Euler Totient:{Color.RESET} {str(phi)[:30]}...")
            print(f"{Color.GREEN}Public Key:{Color.RESET} (e={pub_key[0]}, n={str(pub_key[1])[:15]}...)")
            print(f"{Color.GREEN}Private Key:{Color.RESET} (d={str(priv_key[0])[:15]}..., n={str(priv_key[1])[:15]}...)")

        elif choice == '2':
            if not pub_key:
                print(f"{Color.RED}Please generate keys first (Option 1).{Color.RESET}")
                continue
            last_message = input("Enter message to encrypt (e.g. HELLO WORLD): ")
            ascii_vals = [ord(c) for c in last_message]
            last_encrypted = encrypt_char_by_char(pub_key, last_message)
            
            print(f"\n{Color.YELLOW}Original:{Color.RESET}  {last_message}")
            print(f"{Color.YELLOW}ASCII:{Color.RESET}     {ascii_vals}")
            print(f"{Color.YELLOW}Encrypted:{Color.RESET} {str(last_encrypted)[:60]}... (truncated)")

        elif choice == '3':
            if not priv_key or not last_encrypted:
                print(f"{Color.RED}Please generate keys and encrypt a message first.{Color.RESET}")
                continue
            
            decrypted_ascii, original = decrypt_char_by_char(priv_key, last_encrypted)
            
            print(f"\n{Color.YELLOW}Encrypted{Color.RESET}")
            print("    ↓")
            print(f"{Color.YELLOW}Decrypted ASCII:{Color.RESET} {decrypted_ascii}")
            print("    ↓")
            print(f"{Color.YELLOW}Original Message:{Color.RESET} {original}")

        elif choice == '4':
            if not priv_key:
                print(f"{Color.RED}Please generate keys first.{Color.RESET}")
                continue
            msg_to_sign = input("Enter message to sign: ")
            expected_hash, signature = sign_message(priv_key, msg_to_sign)
            
            # Store globally for verification demo
            global current_sig, current_signed_msg
            current_sig = signature
            current_signed_msg = msg_to_sign
            
            print(f"\n{Color.YELLOW}Original Hash:{Color.RESET} {expected_hash}")
            print(f"{Color.YELLOW}Digital Signature:{Color.RESET} {str(signature)[:60]}... (truncated)")

        elif choice == '5':
            if not pub_key or 'current_sig' not in globals():
                print(f"{Color.RED}Please sign a message first (Option 4).{Color.RESET}")
                continue
            
            print(f"\nVerifying signature for message: '{current_signed_msg}'")
            expected_hash, recovered_hash, is_valid = verify_signature(pub_key, current_signed_msg, current_sig)
            
            print(f"\n{Color.YELLOW}Original Hash{Color.RESET}\n{expected_hash}")
            print("        =")
            print(f"{Color.YELLOW}Recovered Hash{Color.RESET}\n{recovered_hash}")
            
            if is_valid:
                print(f"\n{Color.GREEN}[+] Signature Valid{Color.RESET}")
            else:
                print(f"\n{Color.RED}[-] Signature Invalid{Color.RESET}")

        elif choice == '6':
            print(f"\n{Color.YELLOW}Number\t\tResult{Color.RESET}")
            print("-" * 30)
            for _ in range(10):
                # Generate a mix of potentially prime and composite numbers
                num = random.randint(100, 9999)
                result = "Prime" if miller_rabin(num) else "Composite"
                
                color = Color.GREEN if result == "Prime" else Color.RED
                print(f"{num}\t\t{color}{result}{Color.RESET}")

        elif choice == '7':
            print(f"\n{Color.CYAN}--- Demonstrating Security Risk of Small Primes ---{Color.RESET}")
            # Generate small 24-bit primes
            small_p = generate_large_prime(24)
            small_q = generate_large_prime(24)
            small_n = small_p * small_q
            print(f"Generated Modulus (n) = p * q = {small_n} (approx {small_n.bit_length()} bits)")
            print("An attacker only knows 'n'. Launching Pollard's Rho factorization...")
            
            start_time = datetime.now()
            factor1 = pollards_rho(small_n)
            factor2 = small_n // factor1
            end_time = datetime.now()
            
            time_taken = (end_time - start_time).total_seconds()
            print(f"\n{Color.RED}[!] Factored successfully in {time_taken:.5f} seconds!{Color.RESET}")
            print(f"Factors found: {factor1} and {factor2}")
            print("Conclusion: Small keys are broken instantly. Always use 2048+ bit RSA in the real world.")

        elif choice == '8':
            rsa_secure_chat()

        elif choice == '9':
            print(f"{Color.GREEN}Exiting RSA Security System. Goodbye!{Color.RESET}")
            break
        else:
            print(f"{Color.RED}Invalid option. Please try again.{Color.RESET}")

if __name__ == "__main__":
    # Clear the terminal for a clean UI
    os.system('cls' if os.name == 'nt' else 'clear')
    main()