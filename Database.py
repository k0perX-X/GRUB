from hashlib import md5
import timeset
from threading import Timer

# Обновление времени
t = Timer(3600.0, timeset.settimeyandex())
t.start()
timeset.settimeyandex()

database = {'data': {}}
ips = {}
servers_ips = {}
logins = {'admin': md5('admin'.encode()).hexdigest()}
stack = []
server_logins = {'instance-1': md5('password'.encode()).hexdigest()}