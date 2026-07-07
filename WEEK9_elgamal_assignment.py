import random
# 1. MATHEMATICAL HELPER FUNCTIONS


def is_prime(n, k=5):
    """Miller-Rabin primality test to check if a number is prime."""
    if n < 2: return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n % p == 0: return n == p
    
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
    """Generates a large prime number of a specific bit length."""
    while True:
        p = random.getrandbits(bits)
        if p % 2 != 0 and is_prime(p):
            return p
# 2. ELGAMAL CRYPTOSYSTEM CLASS

class ElGamal:
    def __init__(self, bit_length=512):
        self.bit_length = bit_length
        # Generate Prime (p) and Generator (g)
        self.p = generate_large_prime(bit_length)
        self.g = random.randint(2, self.p - 1)
        
        # Private Key (x): A random integer less than p
        self.x = random.randint(2, self.p - 2)
        
        # Public Key (y): g^x mod p
        self.y = pow(self.g, self.x, self.p)

    def get_public_key(self):
        return (self.p, self.g, self.y)

    def get_private_key(self):
        return self.x

    def encrypt(self, message_str):
        """Encrypts a string message into a ciphertext pair (c1, c2)."""
        # Convert string message to integer
        m = int.from_bytes(message_str.encode('utf-8'), 'big')
        
        if m >= self.p:
            raise ValueError("Message is too large for the current key size.")
            
        # FRESH RANDOM VALUE (k) - Essential for ElGamal security!
        k = random.randint(2, self.p - 2)
        
        # Calculate c1 = g^k mod p
        c1 = pow(self.g, k, self.p)
        
        # Calculate Shared Secret s = y^k mod p
        s = pow(self.y, k, self.p)
        
        # Calculate c2 = m * s mod p
        c2 = (m * s) % self.p
        
        return c1, c2

    def decrypt(self, c1, c2):
        """Decrypts a ciphertext pair (c1, c2) back into the original string."""
        # Recalculate Shared Secret s = c1^x mod p
        s = pow(c1, self.x, self.p)
        
        # Calculate the modular inverse of s using Fermat's Little Theorem
        # Since p is prime, s^(-1) = s^(p-2) mod p
        s_inv = pow(s, self.p - 2, self.p)
        
        # Recover message integer m = c2 * s^(-1) mod p
        m = (c2 * s_inv) % self.p
        
        # Convert integer back to string
        byte_length = (m.bit_length() + 7) // 8
        return m.to_bytes(byte_length, 'big').decode('utf-8')
# 3. EXECUTION AND DEMONSTRATION

def run_elgamal_simulation():
    print("=" * 60)
    print(" " * 15 + "ELGAMAL CRYPTOSYSTEM DEMO")
    print("=" * 60)
    
    # --- 1. Key Generation ---
    print("\n[+] 1. Generating ElGamal Keys (512-bit)...")
    cipher = ElGamal(bit_length=512)
    p, g, y = cipher.get_public_key()
    x = cipher.get_private_key()
    
    print(f"  -> Public Key (p):  {str(p)[:30]}... (truncated)")
    print(f"  -> Public Key (g):  {g}")
    print(f"  -> Public Key (y):  {str(y)[:30]}... (truncated)")
    print(f"  -> Private Key (x): {str(x)[:30]}... (HIDDEN)")

    # --- 2. Encrypting & Decrypting 5 Messages ---
    print("\n" + "=" * 60)
    print("[+] 2. Processing 5 Unique Messages")
    print("=" * 60)
    
    messages = [
        "Operation Midnight is a go.",
        "Target coordinates: 45.92 N, 14.23 E",
        "The eagle has landed safely.",
        "Abort the mission immediately!",
        "Rendezvous at Sector 7G at dawn."
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n--- Message {i} ---")
        print(f"Original Text : '{msg}'")
        
        # Encrypt
        c1, c2 = cipher.encrypt(msg)
        print(f"Ciphertext c1 : {str(c1)[:25]}... (truncated)")
        print(f"Ciphertext c2 : {str(c2)[:25]}... (truncated)")
        
        # Decrypt
        decrypted_msg = cipher.decrypt(c1, c2)
        print(f"Decrypted Text: '{decrypted_msg}'")
        
        # Verification
        assert msg == decrypted_msg, "Decryption failed!"
        print("Status        : [SUCCESS] Match Verified")

    # --- 3. Cryptanalysis Concept Explanation ---
    print("\n" + "=" * 60)
    print("[+] 3. Why is a fresh random value (k) essential?")
    print("=" * 60)
    
    explanation = """
In the ElGamal encryption scheme, the ciphertext consists of two parts:
c1 = g^k mod p
c2 = m * (y^k) mod p

The random integer 'k' is known as the ephemeral (temporary) key. It is 
CRITICAL that a brand new 'k' is generated for every single message.

THE VULNERABILITY (k-Reuse Attack):
If an attacker intercepts two ciphertexts that were encrypted using the 
exact same 'k':
  Ciphertext A: (c1, c2_A) where c2_A = m_A * (y^k) mod p
  Ciphertext B: (c1, c2_B) where c2_B = m_B * (y^k) mod p

Because 'k' was reused, the shared secret (y^k) is identical. 
An attacker can simply divide the two ciphertexts:
  c2_A / c2_B = (m_A * y^k) / (m_B * y^k) = m_A / m_B mod p

This completely cancels out the encryption! The attacker now knows the 
exact mathematical relationship between the two plaintext messages 
(m_A and m_B). If the attacker manages to guess or find out what just 
ONE of the messages is, they instantly know the other message without 
ever needing the private key.

Conclusion: Reusing 'k' turns ElGamal into a deterministic cipher, 
destroying its semantic security.
"""
    print(explanation)

if __name__ == "__main__":
    run_elgamal_simulation()