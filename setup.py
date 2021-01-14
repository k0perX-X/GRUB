try:
    import pip
except:
    print('Please install pip')
    exit()
lose_import = False

try:
    import os.path
except:
    pip.main(['install', 'os'])
    lose_import = True

try:
    import flask
except:
    lose_import = True
    pip.main(['install', 'flask'])

try:
    import json
except:
    lose_import = True
    pip.main(['install', 'json'])

try:
    import logging
except:
    lose_import = True
    pip.main(['install', 'logging'])

try:
    import time
except:
    lose_import = True
    pip.main(['install', 'time'])

try:
    import requests
except:
    lose_import = True
    pip.main(['install', 'requests'])

try:
    import traceback
except:
    lose_import = True
    pip.main(['install', 'traceback'])

try:
    import random
except:
    lose_import = True
    pip.main(['install', 'random'])

try:
    import threading
except:
    lose_import = True
    pip.main(['install', 'threading'])

try:
    import urllib3
except:
    lose_import = True
    pip.main(['install', 'urllib3'])

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

try:
    from Crypto.Cipher import DES
except:
    lose_import = True
    pip.main(['install', 'pycryptodome'])
    pip.main(['install', 'pycryptodomex'])

from sys import argv

if '--only-install' not in argv:
    import output.setup
