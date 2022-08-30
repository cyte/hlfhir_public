from Crypto.Cipher import AES
import globals as globals,sys
key_location = "crypt/crypt_key.bin"



def set_key():
    file_in = open(key_location, "rb") # Read bytes
    globals.crypto_key = file_in.read() # This key should be the same
    file_in.close()


def encrypt(data,output_file):
    cipher = AES.new(globals.crypto_key, AES.MODE_CFB) # CFB mode
    ciphered_data = cipher.encrypt(data) # Only need to encrypt the data, no padding required for this mode
    file_out = open(output_file, "wb")
    file_out.write(cipher.iv)
    file_out.write(ciphered_data)
    file_out.close()


#input_file = 'encrypted.bin'

def decrypt(input_file):
    file_in = open(input_file, 'rb')
    iv = file_in.read(16)
    ciphered_data = file_in.read()
    file_in.close()

    cipher = AES.new(globals.crypto_key, AES.MODE_CFB, iv=iv)
    encoding = 'utf-8'
    original_data = cipher.decrypt(ciphered_data).decode(encoding) # No need to un-pad
    return original_data

 # (Example of how to use this to encrypt data on the fly)
#x = b'''123456
# 7891234'''
#key = set_key()
#encrypt(x,"enc_b41_200rows.bin")