from random import randint
f = open('encrypt_keys.py', 'w')
f.write('encrypt_keys = [\n')
for i in range(1000):
	f.write('\t' + str(bytes([randint(0, 255) for i in range(8)])) + ",\n")
f.write(']')
f.close()
print('encrypt_keys.py has been generated.')
