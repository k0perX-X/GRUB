try:
    import pip
except:
    print('Please install pip')
    exit()
lose_import = False

try:
    from colorama import Fore, Back, Style
except:
    lose_import = True
    pip.main(['install', 'colorama'])
    from colorama import Fore, Back, Style

try:
    from hashlib import md5
except:
    lose_import = True
    pip.main(['install', 'hashlib'])
    from hashlib import md5

from random import randint

if lose_import:
    print('\n\n\n')
print(Fore.BLUE + 'Welcome to the GRUB setup\n' + Style.RESET_ALL)

while True:
    login = input('Enter the name of your server (the names within the same network must not be the same): ')
    if login.find("'") != -1:
        print("Please enter a name without the symbol '")
    else:
        break
print()

first = False
while True:
    s = input('Is this your first server on the network (y/n)? ')
    s = s.strip()
    if s[0] == 'y' or s[0] == 'Y':
        first = True
        break
    elif s[0] == 'n' or s[0] == 'N':
        first = False
        break
print()

start_leader = ''
if not first:
    while True:
        start_leader = input('Enter the ip (url) of the server already on the network: ')
        if login.find("'") != -1:
            print("Please enter a name without the symbol '")
        else:
            break
    print()

tf = True
while tf:
    base_cycle_time = input('Enter base cycle time (must be common to one network) (default 1 second): ')
    if base_cycle_time == '':
        base_cycle_time = 1
        tf = False
    else:
        try:
            base_cycle_time = int(base_cycle_time)
            tf = False
        except:
            pass
print()

tf = True
while tf:
    multiplier_update_cycle_time = input(
        'Enter the number of cycles after which the cycle time will be updated (must be common to one network) (default 100): ')
    if multiplier_update_cycle_time == '':
        multiplier_update_cycle_time = 100
        tf = False
    else:
        try:
            multiplier_update_cycle_time = int(multiplier_update_cycle_time)
            tf = False
        except:
            pass
print()

print('''Enter usernames and their passwords. 
Example: name1: password1, name2: password2''')
print(Fore.RED + '''Attention! 
Always comma and 1 space between users and colon and 1 space between name and password
name1, name 1, name1 , - are not the same''' + Style.RESET_ALL)
s = input()
user_logins = {}
for ss in s.split(', '):
    ss = ss.split(': ')
    user_logins[ss[0]] = md5(ss[1].encode('utf32')).hexdigest()
print(f'You entered: {user_logins}\n')

print('''Enter administrator account for this server. 
Example: name1, name2''')
print(Fore.RED + '''Attention! 
Always comma and 1 space between names
name1, name 1, name1 , - are not the same''' + Style.RESET_ALL)
s = input()
admin_logins = []
for ss in s.split(', '):
    admin_logins.append(ss)
print(f'You entered: {admin_logins}\n')

print('''Enter the names of the databases. 
Example: name1, name2''')
print(Fore.RED + '''Attention! 
Always comma and 1 space between names
name1, name 1, name1 , - are not the same''' + Style.RESET_ALL)
s = input()
databases = []
for ss in s.split(', '):
    databases.append(ss)
print(f'You entered: {databases}\n')

debug = False
while True:
    s = input('Start server in debug mode? (y/n)? ')
    if s[0] == 'y' or s[0] == 'Y':
        debug = True
        break
    elif s[0] == 'n' or s[0] == 'N':
        debug = False
        break
print()

if __name__ == '__main__':
    f = open('config.py', 'w', encoding='utf8')
else:
    f = open('output/config.py', 'w', encoding='utf8')
s = f'''login = '{login}'
base_cycle_time = {base_cycle_time}
multiplier_update_cycle_time = {multiplier_update_cycle_time}
first = {first}
start_leader = '{start_leader}'
debug = {debug}
'''
f.write(s)
f.close()

print('Your finished config file:\n' + s)
if __name__ == '__main__':
    f = open('database.py', 'w', encoding='utf32')
else:
    f = open('output/database.py', 'w', encoding='utf32')
f.write('{')
for data in databases:
    if data.find("'") == -1:
        f.write(f"'{data}': {{}}, ")
    else:
        f.write(f'"{data}": {{}}, ')
f.write('}')
f.close()

if __name__ == '__main__':
    f = open('user_logins.py', 'w', encoding='utf32')
else:
    f = open('output/user_logins.py', 'w', encoding='utf32')
f.write(str(user_logins))
f.close()

if __name__ == '__main__':
    f = open('admin_logins.py', 'w', encoding='utf32')
else:
    f = open('output/admin_logins.py', 'w', encoding='utf32')
f.write(str(admin_logins))
f.close()

if __name__ == '__main__':
    f = open('encrypt_keys.py', 'w')
else:
    f = open('output/encrypt_keys.py', 'w')
f.write('encrypt_keys = [\n')
for i in range(1000):
    f.write('\t' + str(bytes([randint(0, 255) for i in range(8)])) + ",\n")
f.write(']')
f.close()
print('encrypt_keys.py has been generated.')

if __name__ == '__main__':
    print(Fore.RED + 'You can change the config in config.py file.' + Style.RESET_ALL)
    if not first:
        print(Fore.RED +
              'REMEMBER TO COPY THE FILE encrypt_keys.py FROM THE ORIGINAL SERVER ON THE NETWORK.' + Style.RESET_ALL)
else:
    print(Fore.RED + 'You can change the config in output/config.py file.' + Style.RESET_ALL)
    if not first:
        print(Fore.RED +
              'REMEMBER TO COPY THE FILE output/encrypt_keys.py FROM THE ORIGINAL SERVER ON THE NETWORK.' +
              Style.RESET_ALL)
print()
