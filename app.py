from flask import Flask, request
import json
from Database import database, ips, logins, stack, server_logins, server_ips, leader, leader_stack
import logging
import time
from hashlib import md5
import requests
import traceback
from crypt import decrypt, encrypt
from random import randint

# Коды операций
# 1 - добавить элемент
# 2 - удалить элемент


app = Flask(__name__)
logging.basicConfig(filename="log.txt", level=logging.WARNING)


# Общение извне
@app.route("/auth", methods=['POST'])
def auth():
	# {
	# 	'login': 'admin',
	# 	'password': 'admin'
	#   'ip': "0.0.0.0"
	# }
	try:
		# преобразование json запроса
		try:
			r = json.loads(request.data)
		except Exception as e:
			logging.warning(time.ctime(time.time()) + " json recognition - not json")
			return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

		# Проверка полноты json
		if 'login' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - login")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "login"}
		if 'password' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - password")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "password"}
		if 'ip' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - ip")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "password"}

		# Проверка существования пользователя
		if r['login'] not in logins:
			logging.warning(time.ctime(time.time()) + " wrong login")
			return {"status": "error", "type error": "wrong login/password"}

		# Проверка пароля
		if md5(r['password'].encode()).hexdigest() != logins[r['login']]:
			logging.warning(time.ctime(time.time()) + " wrong password")
			return {"status": "error", "type error": "wrong login/password"}

		# Добавить в словарь
		ips[r['login']] = r['ip']

		return {'system': 'ok', "time": time.time()}
	except Exception as e:
		logging.error(time.ctime(time.time()) + " " + traceback.format_exc())
		return {"status": "error", "type error": "unknown error"}


@app.route("/add", methods=['POST'])
def add():
	# {
	# 	'dictionary name': 'data',
	# 	'amount of elements': 2,
	# 	'values': {
	# 		'123': 123,
	# 		2345: 2345
	# 	}}
	try:
		# преобразование json запроса
		try:
			r = json.loads(request.data)
		except Exception as e:
			logging.warning(time.ctime(time.time()) + " json recognition - not json")
			return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

		# проверка аунтификации
		if 'ip' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - ip")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "password"}
		if r['ip'] not in ips.values():
			return {"status": "error", "type error": "not autified"}

		# проверка dictionary name
		if 'dictionary name' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - dictionary name")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "dictionary name"}
		if r['dictionary name'] not in database:
			logging.warning(time.ctime(time.time()) + " dictionary name - dictionary does not exist")
			return {"status": "error", "type error": "dictionary does not exist"}

		# проверка значений
		if 'amount of elements' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - amount of elements")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "amount of elements"}
		if type(r['amount of elements']) != int:
			logging.warning(time.ctime(time.time()) + " amount of elements - not a number")
			return {"status": "error", "type error": "amount of elements - not a number"}
		if 'values' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - values")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "values"}
		if type(r['values']) != dict:
			logging.warning(time.ctime(time.time()) + " values - not a dict")
			return {"status": "error", "type error": "values - not a dict"}

		# Приравнивание
		#database[r['dictionary name']] = {**database[r['dictionary name']], **r['values']}
		stack.append([time.time(), 1, r['dictionary name'], r['values']])

		# Сообщить другим серверам

		# Вывод
		return {"status": "ok", "dictionary name": r['dictionary name'], "time": time.time()}
	except Exception as e:
		logging.error(time.ctime(time.time()) + " " + traceback.format_exc())
		return {"status": "error", "type error": "unknown error"}


@app.route("/databases", methods=['POST'])
def data():
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		logging.warning(time.ctime(time.time()) + " json recognition - not json")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	# проверка аунтификации
	if 'ip' not in r:
		logging.warning(time.ctime(time.time()) + " json recognition - json is not full - ip")
		return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
				"json is not full": "password"}
	if r['ip'] not in ips.values():
		return {"status": "error", "type error": "not autified"}

	return {**database, "time": time.time(), 'status': 'ok'}


@app.route("/delete", methods=['POST'])
def delete():
	# }
	# 'dictionary name': 'data',
	# 'key': '123'
	# }
	try:
		# преобразование json запроса
		try:
			r = json.loads(request.data)
		except:
			logging.warning(time.ctime(time.time()) + " json recognition - not json")
			return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

		# проверка аунтификации
		if 'ip' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - ip")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "password"}
		if r['ip'] not in ips.values():
			return {"status": "error", "type error": "not autified"}

		# проверка dictionary name
		if 'dictionary name' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - dictionary name")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "dictionary name"}
		if r['dictionary name'] not in database:
			logging.warning(time.ctime(time.time()) + " dictionary name - dictionary does not exist")
			return {"status": "error", "type error": "dictionary does not exist"}

		# проверка key
		if r['key'] not in database[r['dictionary name']]:
			logging.warning(time.ctime(time.time()) + " key - key does not exist")
			return {"status": "error", "type error": "key"}

		# удаление
		# del database[r['dictionary name']][r['key']]
		stack.append([time.time(), 2, r['dictionary name'], r['key']])

		return {"status": "done", "dictionary name": r['dictionary name'], "time": time.time()}
	except Exception as e:
		logging.error(time.ctime(time.time()) + " " + traceback.format_exc())
		return {"status": "error", "type error": "unknown error"}


# Общение внутри
# Ответы
@app.route("/servers/auth", methods=['POST'])
def server_auth():
	try:
		# преобразование json запроса
		try:
			r = json.loads(request.data)
		except Exception as e:
			logging.warning(time.ctime(time.time()) + " json recognition - not json")
			return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

		# encrypt
		try:
			r = decrypt(r['1'], eval(r['2']))
		except Exception as e:
			logging.warning(time.ctime(time.time()) + " json recognition - encode")
			return {"status": "error", "type error": "json recognition", "json recognition": "encode"}

		# преобразование json запроса
		try:
			r = json.loads(r)
		except Exception as e:
			logging.warning(time.ctime(time.time()) + " json recognition - not json")
			return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

		# Проверка полноты json
		if 'login' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - login")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "login"}
		if 'password' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - password")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "password"}
		if 'ip' not in r:
			logging.warning(time.ctime(time.time()) + " json recognition - json is not full - ip")
			return {"status": "error", "type error": "json recognition", "json recognition": "json is not full",
					"json is not full": "password"}

		# Проверка существования пользователя
		if r['login'] not in server_logins:
			logging.warning(time.ctime(time.time()) + " wrong login")
			return {"status": "error", "type error": "wrong login/password"}

		# Проверка пароля
		if md5(r['password'].encode()).hexdigest() != server_logins[r['login']]:
			logging.warning(time.ctime(time.time()) + " wrong password")
			return {"status": "error", "type error": "wrong login/password"}

		# Добавить в словарь
		server_ips[r['login']] = r['ip']

		return {'status': 'auntified', 'ips': {**server_ips}, "time": time.time(), 'leader': {**leader}}
	except Exception as e:
		logging.error(time.ctime(time.time()) + " " + traceback.format_exc())
		return {"status": "error", "type error": "unknown error"}


# Лидер ответ на stack
@app.route('/servers/leader', methods=['POST'])
def func_leader():
	r = json.loads(request.data)
	r = decrypt(r['1'], eval(r['2']))
	r = json.loads(r)
	global leader_stack
	leader_stack += r
	return {"status": "ok"}


# Фоловер ответ на database
@app.route("/servers/follower", methods=['POST'])
def func_follower():
	try:
		r = json.loads(request.data)
		r = decrypt(r['1'], eval(r['2']))
		r = json.loads(r)
		global database
		database = {**database, **r['database']}
		global server_ips
		server_ips = {**server_ips, **r['servers_ips']}
		global ips
		ips = {**ips, **r['ips']}
		global logins
		logins = {**logins, **r['logins']}
		global server_logins
		server_logins = {**server_logins, **r['server_logins']}
		send_stack()
		return {"status": "ok"}
	except Exception as e:
		logging.error(time.ctime(time.time()) + " " + traceback.format_exc())
		return {"status": "error", "type error": "unknown error"}


def send_stack():
	try:
		x = randint(0, 999)
		r = requests.post(f"https://{leader['ip']}/servers/leader", verify=False, json={
			'1': x,
			'2': str(encrypt(x, json.dumps(stack).encode('utf8')))
		}).json()
		if r['status'] != 'ok':
			raise Exception
	except Exception as e:
		#
		# НЕ ДОДЕЛАНО!!!!!!!!!!!!!!!!!!!!
		#
		logging.warning()


def send_data():
	try:
		leader_stack.sort(key=lambda y: y[0])
		for i in leader_stack:
			if i[1] == 1:
				database[i[2]] = {**database[i[2]], **i[3]}
			elif i[1] == 2:
				del database[i[2]][i[3]]
		j = {
			'database': database,
			'server_ips': server_ips,
			'ips': ips,
			'logins': logins,
			'server_logins': server_logins
		}
		x = randint(0, 999)
		for i in server_ips.values():
			if i != leader['ip']:
				try:
					r = requests.post(f"https://{i}/servers/follower", verify=False, json={
						'1': x,
						'2': str(encrypt(x, json.dumps(j).encode('utf8')))
					}).json()
					if r['status'] != 'ok':
						raise Exception
				except Exception as e:
					#
					# НЕ ДОДЕЛАНО!!!!!!!!!!!!!!!!!!!!
					#
					logging.warning()
	except Exception as e:
		#
		# НЕ ДОДЕЛАНО!!!!!!!!!!!!!!!!!!!!
		#
		logging.warning()


if __name__ == '__main__':
	app.run()
