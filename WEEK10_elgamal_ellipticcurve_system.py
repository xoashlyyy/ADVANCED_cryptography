import random
import time
import hashlib
import math
import os

try:
    from ecdsa import SigningKey, SECP256k1
    HAS_ECDSA = True
except ImportError:
    HAS_ECDSA = False
# HELPER MATHEMATICS

def is_prime(n, k=5):
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
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def generate_prime(bits=256):
    while True:
        p = random.getrandbits(bits)
        if p % 2 != 0 and is_prime(p): return p
# ELGAMAL SYSTEM

class ElGamal:
    def __init__(self, bits=256):
        self.p = generate_prime(bits)
        self.g = random.randint(2, self.p - 1)
        self.x = random.randint(2, self.p - 2) # Private key
        self.y = pow(self.g, self.x, self.p)   # Public key

    def encrypt(self, message, k_val=None):
        m = int.from_bytes(message.encode(), 'big')
        k = k_val if k_val else random.randint(2, self.p - 2)
        c1 = pow(self.g, k, self.p)
        s = pow(self.y, k, self.p)
        c2 = (m * s) % self.p
        return k, c1, c2

    def decrypt(self, c1, c2):
        s = pow(c1, self.x, self.p)
        s_inv = pow(s, self.p - 2, self.p) # Fermat's Little Theorem
        m = (c2 * s_inv) % self.p
        return m.to_bytes((m.bit_length() + 7) // 8, 'big').decode()
# MINI RSA SYSTEM (FOR BENCHMARKING)

class MiniRSA:
    def __init__(self, bits=128):
        p, q = generate_prime(bits), generate_prime(bits)
        self.n = p * q
        phi = (p - 1) * (q - 1)
        self.e = 65537
        self.d = pow(self.e, -1, phi)

    def encrypt(self, message):
        m = int.from_bytes(message.encode(), 'big')
        return pow(m, self.e, self.n)

    def decrypt(self, c):
        m = pow(c, self.d, self.n)
        return m.to_bytes((m.bit_length() + 7) // 8, 'big').decode()
# MAIN MENU APPLICATION

def main():
    cipher = None
    last_ciphertext = None

    while True:
    
        print("      ELGAMAL SECURITY SYSTEM      ")
  
        print("1 Generate Keys")
        print("2 Encrypt Message")
        print("3 Decrypt Message")
        print("4 Compare RSA vs ElGamal & Randomness Demo")
        print("5 ECC Demo (ECDSA Library)")
        print("6 Exit")
        
        choice = input("Select an option: ")

        if choice == '1':
            print("\nGenerating ElGamal Keys...")
            cipher = ElGamal(bits=256)
            print(f"Prime (p):     {str(cipher.p)[:25]}...")
            print(f"Generator (g): {cipher.g}")
            print(f"Private Key:   {str(cipher.x)[:25]}...")
            print(f"Public Key:    {str(cipher.y)[:25]}...")

        elif choice == '2':
            if not cipher:
                print("Generate keys first!")
                continue
            msg = input("Enter message (e.g. THIS IS SECRET): ")
            k, c1, c2 = cipher.encrypt(msg)
            last_ciphertext = (c1, c2)
            print(f"\nRandom k: {str(k)[:15]}...")
            print(f"Ciphertext C1: {str(c1)[:25]}...")
            print(f"Ciphertext C2: {str(c2)[:25]}...")

        elif choice == '3':
            if not cipher or not last_ciphertext:
                print("Encrypt a message first!")
                continue
            decrypted = cipher.decrypt(*last_ciphertext)
            print(f"\nOriginal Message: {decrypted}")

        elif choice == '4':
            if not cipher:
                print("Generate ElGamal keys first!")
                continue
            
            print("\n--- Part D: Randomness Demonstration ---")
            test_msg = "THIS IS SECRET"
            print(f"Message: {test_msg}\n")
            for i in range(1, 6):
                k, c1, c2 = cipher.encrypt(test_msg)
                print(f"Run {i} | C1: {str(c1)[:10]}... | C2: {str(c2)[:10]}...")
            
            print("\nDiscussion: ElGamal produces different ciphertexts because it uses a fresh, random ephemeral key (k) for every single encryption. This prevents frequency analysis.")

            print("\n--- Part E: RSA vs ElGamal Benchmark ---")
            print("Measuring execution times (in seconds)...")
            
            # RSA Benchmark
            t0 = time.time()
            rsa = MiniRSA()
            rsa_gen = time.time() - t0
            
            t0 = time.time()
            rsa_c = rsa.encrypt(test_msg)
            rsa_enc = time.time() - t0
            
            t0 = time.time()
            rsa.decrypt(rsa_c)
            rsa_dec = time.time() - t0

            # ElGamal Benchmark
            t0 = time.time()
            elg = ElGamal()
            elg_gen = time.time() - t0
            
            t0 = time.time()
            _, elg_c1, elg_c2 = elg.encrypt(test_msg)
            elg_enc = time.time() - t0
            
            t0 = time.time()
            elg.decrypt(elg_c1, elg_c2)
            elg_dec = time.time() - t0

            print(f"{'Algorithm':<15} | {'Key Gen':<10} | {'Encrypt':<10} | {'Decrypt':<10}")
            print("-" * 55)
            print(f"{'RSA':<15} | {rsa_gen:.6f}   | {rsa_enc:.6f}   | {rsa_dec:.6f}")
            print(f"{'ElGamal':<15} | {elg_gen:.6f}   | {elg_enc:.6f}   | {elg_dec:.6f}")
            print("\nExplanation: RSA is generally faster at encryption (using small public exponent e) but slower at key generation. ElGamal requires two heavy modular exponentiations during encryption, making it slower to encrypt, but generation of p and g is standard.")

        elif choice == '5':
            print("\n--- Part F: ECC Demonstration ---")
            if not HAS_ECDSA:
                print("Please install the ecdsa library: pip install ecdsa")
                continue
            
            print("Generating ECC SECP256k1 Key Pair...")
            sk = SigningKey.generate(curve=SECP256k1)
            vk = sk.verifying_key
            
            print(f"Private Key: {sk.to_string().hex()[:30]}...")
            print(f"Public Key:  {vk.to_string().hex()[:30]}...")
            
            msg = b"Secure payload approved."
            print(f"\nSigning message: '{msg.decode()}'")
            signature = sk.sign(msg)
            print(f"Digital Signature: {signature.hex()[:40]}...")
            
            print("Verifying Signature...")
            is_valid = vk.verify(signature, msg)
            print("Status:", "VALID" if is_valid else "INVALID")

        elif choice == '6':
            print("Exiting...")
            break

if __name__ == "__main__":
    main()