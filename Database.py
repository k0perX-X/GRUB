from hashlib import md5
import timeset
from threading import Timer

# Обновление времени
t = Timer(3600.0, timeset.settimeyandex())
t.start()
timeset.settimeyandex()

database = {'data': {}}
ips = {}
logins = {'admin': md5('admin'.encode()).hexdigest()}