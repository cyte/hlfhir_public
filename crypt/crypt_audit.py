from crypt.crypt import *

set_key()
print("%s: %d" %(sys.argv[1],len(list(filter(None,decrypt(sys.argv[1]).split('\n'))))))