import sys
import datetime
import requests
from threading import Timer

def _linux_set_time(time_tuple):
	import ctypes
	import ctypes.util
	import time
	CLOCK_REALTIME = 0

	class timespec(ctypes.Structure):
		_fields_ = [("tv_sec", ctypes.c_long),
					("tv_nsec", ctypes.c_long)]

	librt = ctypes.CDLL(ctypes.util.find_library("rt"))

	ts = timespec()
	ts.tv_sec = int(time.mktime(datetime.datetime(*time_tuple[:6]).timetuple()))
	ts.tv_nsec = time_tuple[6] * 1000000  # Millisecond to nanosecond

	librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))


def timeset(unixtime):
	from datetime import datetime
	a = []
	for i in datetime.timetuple(datetime.fromtimestamp(float(unixtime))):
		a.append(i)
	time_tuple = (
		a[0],  # Year
		a[1],  # Month
		a[2],  # Day
		a[3],  # Hour
		a[4],  # Minute
		a[5],  # Second
		int(unixtime * 1000 % 1000),  # Millisecond
		)
	#print(time_tuple)
	if sys.platform == 'linux':
		_linux_set_time(time_tuple)


def settimeyandex():
	timeset(float(requests.get('https://yandex.com/time/sync.json').json()["time"]) / 1000)
	set_time = Timer(3600.0, settimeyandex)
	set_time.start()


if __name__ == "__main__":
	settimeyandex()