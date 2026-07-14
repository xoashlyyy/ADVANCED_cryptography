from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

def main():
    print(" RSA Digital Signature Tool ")
    
    # 1. Generate a 2048-bit RSA key pair
    print("Generating 2048-bit keys...\n")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    
    # Print the Private Key
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    print(" YOUR PRIVATE KEY ")
    print(pem_private.decode('utf-8'))
    
    # Print the Public Key
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print("YOUR PUBLIC KEY ")
    print(pem_public.decode('utf-8'))
    
    # 2. Prompt the user for a message
    message = input("\n Enter a message to sign: ")
    msg_bytes = message.encode('utf-8')
    
    # 3. Hash and sign the message using the private key
    print("\nSigning the message...")
    signature = private_key.sign(
        msg_bytes,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    print(f"Signature generated: {signature.hex()[:40]}...")
    
    # 4. Verify the original signature
    print("\n Test 1: Verifying Original Message ")
    try:
        public_key.verify(
            signature,
            msg_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        print(" Signature is valid. Message is authentic.")
    except Exception:
        print(" Signature is invalid.")
        
    # 5. Modify one character MANUALLY and verify again
    print("\nTest 2: Tampering with the Message ")
   
    fake_message = input("Enter a tampered version of your message (change just one letter!): ")
    fake_bytes = fake_message.encode('utf-8')
    
    try:
        public_key.verify(
            signature,
            fake_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        print(" Signature is valid.")
    except Exception:
        print(" Signature verification failed! The message was tampered with.")
        
    print("-" * 34)

if __name__ == "__main__":
    main()