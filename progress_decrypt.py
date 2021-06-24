# Decrypt prowin32.exe ASCII hex username / passwords that are "encrypted" when passed as startup parameters.
# usage: python progress_decrypt.py oech1::deadbeefcafe

# This will do the same thing: 
# https://gchq.github.io/CyberChef/#recipe=From_Hex('Auto')XOR(%7B'option':'UTF8','string':'PROGRESS'%7D,'Standard',false)

import sys

def decrypt( src ):
    return do_crypto( bytearray.fromhex(src) )
    
def do_crypto( src ):
    key_bytes = bytes('PROGRESS', 'utf-8')
    key_len = len(key_bytes)
    src_len = len( src )
    dest_bytes = []
    key_ct = 0

    for ct in range(0, src_len ):
       if key_ct >= key_len:
         key_ct = 0
       dest_bytes.append( src[ct] ^ key_bytes[key_ct] )
       key_ct += 1 
    return bytearray(dest_bytes).decode('utf-8');

src = sys.argv[1]
if src.startswith('oech1::'):
    src = src.split(':')[3]

print( decrypt( src ) )

