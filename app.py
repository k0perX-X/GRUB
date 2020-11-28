from flask import Flask, request
import json
from Database import database, ips, logins, stack, server_logins, servers_ips
import logging
import time
from hashlib import md5
import requests
import traceback
from crypt import decrypt, encrypt


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

		return {'system': 'auntified', "time": time.time()}
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
		# database[r['dictionary name']] = {**database[r['dictionary name']], **r['values']}
		stack.append([time.time(), 1, r['values']])

		# Сообщить другим серверам

		# Вывод
		return {"status": "done", "dictionary name": r['dictionary name'],
				"updated dictionary": database[r['dictionary name']], "time": time.time()}
	except Exception as e:
		logging.error(time.ctime(time.time()) + " " + traceback.format_exc())
		return {"status": "error", "type error": "unknown error"}


@app.route("/databases", methods=['GET'])
def data():
	# проверка аунтификации
	if request.remote_addr not in ips.values():
		return {"status": "error", "type error": "not autified"}
	return {**database, "time": time.time()}


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

		return {"status": "done", "dictionary name": r['dictionary name'],
				"updated dictionary": database[r['dictionary name']], "time": time.time()}
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
		servers_ips[r['login']] = r['ip']

		return {'system': 'auntified', 'ips': {**servers_ips}, "time": time.time()}
	except Exception as e:
		logging.error(time.ctime(time.time()) + " " + traceback.format_exc())
		return {"status": "error", "type error": "unknown error"}


if __name__ == '__main__':
	app.run()
