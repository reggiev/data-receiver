import os
import rsa
import base64

def encrypt(data):
    """
        item: string to be encrypted
        pub_key: pem key to use for encryption
    """
    n = 100
    delimeter = "#"
    pub_key = rsa.PublicKey._load_pkcs1_pem(os.environ.get('pub_key', ""))
    data = str(data)

    # slice the item so that it will fit to the encryption
    chunks = [data[i:i+n] for i in range(0, len(data), n)]
    return delimeter.join(base64.b64encode(rsa.encrypt(chunk.encode(), pub_key)).decode('UTF-8') for chunk in chunks)
