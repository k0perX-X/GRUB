from flask import Flask, request
import json
import logging
import time
import requests
import traceback
from crypt import decrypt, encrypt, user_logins, login, first, start_leader, debug
from random import randint, choice
import timeset
from threading import Timer
import urllib3

urllib3.disable_warnings()  # отключает уведомление о не верифицированном ssl

# TODO: обновление cycle_time
# TODO: вывод в логфайл полученные данные если ошибка в json запросе
# TODO: параллельные запросы в лидере
# TODO: улучшить криптографию
# TODO: debug режим

# data
stack = []
leader = ''
server_ips = {
	login: requests.get('https://api.ipify.org?format=json').json()['ip']
}
database = {
	'data': {
	}
}
myip = requests.get('https://api.ipify.org?format=json').json()['ip']
cycle_time = 1
last_time_elections = time.time()
votes = {}
if debug:
	debug_dict = {}

app = Flask(__name__)
logging.basicConfig(filename="log.txt", level=logging.WARNING)


# Функции голосования
def vote():
	global last_time_elections
	global ballot
	global leader
	global votes

	# рассылка голоса
	my_vote = choice([*server_ips.values()])
	j = {
		'ip': myip,
		'vote': my_vote
	}
	res = []
	for ip in server_ips.values():
		x = randint(0, 999)
		if ip != myip:
			try:
				r = requests.post(f"https://{ip}/servers/votes", verify=False, json={
					'1': x,
					'2': str(encrypt(x, json.dumps(j).encode('utf8')))
				}).json()
				res.append(r)
			except:
				logging.error(f'vote - {ip} \n {traceback.format_exc()}')

	# проверка на ошибку голосования
	for i in res:
		if i['status'] == 'leader':
			leader = i['leader']
			ballot.cancel()
			ballot = Timer(6 * cycle_time, vote)
			ballot.start()
			return

	time.sleep(3 * cycle_time)
	new_votes = {}
	votes[myip] = my_vote

	# подсчёт голосов
	for v in votes.values():
		if v not in new_votes:
			new_votes[v] = 1
		else:
			new_votes[v] += 1
	votes = {}
	max_ip = []
	max_value = 0
	for i in new_votes:
		if new_votes[i] > max_value:
			max_value = new_votes[i]
			max_ip = [i]
		elif new_votes[i] == max_value:
			max_ip.append(i)

	# проверка правильности голосования
	if len(max_ip) > 1:
		time.sleep(cycle_time)
		vote()

	# подведение результатов
	if max_ip[0] == myip:

		# если выбрали меня
		res = []
		for ip in server_ips.values():
			x = randint(0, 999)
			if ip == myip:
				try:
					r = requests.post(f"http://localhost:5000/servers/new_leader", verify=False, json={
						'1': x,
						'2': str(encrypt(x, json.dumps({
							'status': 'ok',
							'ip': myip
						}).encode('utf8')))
					}).json()
					res.append(r)  # Собираю резы на всякий случай
				except:
					logging.error(f'vote - new_leader - localhost - {ip} \n {traceback.format_exc()}')
			else:
				try:
					r = requests.post(f"https://{ip}/servers/new_leader", verify=False, json={
						'1': x,
						'2': str(encrypt(x, json.dumps({
							'status': 'ok',
							'ip': myip
						}).encode('utf8')))
					}).json()
					res.append(r)  # Собираю резы на всякий случай
				except:
					logging.error(f'vote - new_leader - {ip} \n {traceback.format_exc()}')
		time.sleep(3 * cycle_time)
		# запуск циклов
		global leader_cycle
		leader_cycle = Timer(cycle_time, func_leader)
		leader_cycle.start()
		ballot.cancel()
		ballot = Timer(6 * cycle_time, vote)
		ballot.start()


	else:
		# если выбрали не меня
		time.sleep(3 * cycle_time)
		if time.time() - 4 * cycle_time >= last_time_elections:
			vote()
		else:
			last_time_elections = time.time()
			ballot.cancel()
			ballot = Timer(6 * cycle_time, vote)
			ballot.start()


@app.route('/servers/new_leader', methods=['POST'])
def new_leader():
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "new_leader - json recognition - not json")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	# encrypt
	try:
		r = decrypt(r['1'], eval(r['2']))
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "new_leader - json recognition - encode")
		return {"status": "error", "type error": "json recognition", "json recognition": "encode"}

	# преобразование json запроса
	try:
		r = json.loads(r)
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "new_leader - json recognition - not json")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	global leader
	leader = r['ip']

	global last_time_elections
	last_time_elections = time.time()
	return {'status': 'ok'}


@app.route('/servers/votes', methods=['POST'])
def func_votes():
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "func_votes - json recognition - not json")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	# encrypt
	try:
		r = decrypt(r['1'], eval(r['2']))
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "func_votes - json recognition - encode")
		return {"status": "error", "type error": "json recognition", "json recognition": "encode"}

	# преобразование json запроса
	try:
		r = json.loads(r)
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "func_votes - json recognition - not json")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	if time.time() - 3 * cycle_time < last_time_elections:
		return {'status': 'leader', 'leader': leader}

	if leader == myip:
		leader_cycle.cancel()
		vote()

	votes[r['ip']] = r['vote']
	return {'status': 'ok'}


# Функция лидера
def func_leader():
	global leader_cycle
	leader_cycle.cancel()
	leader_cycle = Timer(cycle_time, func_leader)
	leader_cycle.start()
	# Создаём запрос
	j = {
		'ip': myip,
		'data': {
			'database': database,
			'server_ips': server_ips,
			'cycle_time': cycle_time
		}
	}
	res = []

	# рассылаем запрос всем
	for ip in server_ips.values():
		if ip == myip:
			x = randint(0, 999)
			r = requests.post(f"http://localhost:5000/servers/follower", verify=False, json={
				'1': x,
				'2': str(encrypt(x, json.dumps(j).encode('utf8')))
			}).json()
			if debug:
				debug_dict['leader'] = r
			r = decrypt(r['1'], eval(r['2']))
			r = json.loads(r)
			res += r
		else:
			x = randint(0, 999)
			try:
				r = requests.post(f"https://{ip}/servers/follower", verify=False, json={
					'1': x,
					'2': str(encrypt(x, json.dumps(j).encode('utf8')))
				}).json()
				r = decrypt(r['1'], eval(r['2']))
				r = json.loads(r)
				res += r
				global ballot
				ballot.cancel()
				ballot = Timer(6 * cycle_time, vote)
				ballot.start()
			except:
				logging.warning(f'leader - {ip} \n {traceback.format_exc()}')

	# обработка полученных стеков
	res.sort(key=lambda y: y[0])
	for deystv in res:
		if deystv[1] == 1:
			database[deystv[2]] = {**database[deystv[2]], **deystv[3]}
		elif deystv[1] == 2:
			for element in deystv[3]:
				try:
					del database[deystv[2]][element]
				except:
					pass


# Функция фоловера
@app.route('/servers/follower', methods=['POST'])
def follower():
	global ballot
	global server_ips
	global cycle_time

	r = json.loads(request.data)
	r = decrypt(r['1'], eval(r['2']))
	r = json.loads(r)
	if r['ip'] == leader:
		if leader != myip:
			ballot.cancel()
			ballot = Timer(6 * cycle_time, vote)
			ballot.start()
		for Data in r['data']['database']:
			database[Data] = r['data']['database'][Data]
		server_ips = r['data']['server_ips']
		cycle_time = r['data']['cycle_time']
		global stack
		new_stack = stack
		stack = []
		x = randint(0, 999)
		return {
			'1': x,
			'2': str(encrypt(x, json.dumps(new_stack).encode('utf8')))
		}
	return {'status': 'not leader'}


# аутентификация нового сервера
@app.route('/servers/auth', methods=['POST'])
def auth_server():
	# {
	# 	'1': x,
	# 	'2': {
	# 		'ip'
	# 		'login'
	# 	}
	# }
	if myip == leader:
		try:
			r = json.loads(request.data)
			r = decrypt(r['1'], eval(r['2']))
			r = json.loads(r)
			server_ips[r['login']] = r['ip']
			return {'status': 'ok'}
		except:
			return {'status': 'error'}
	else:
		x = randint(0, 999)
		return {
			'status': 'not leader',
			'leader': {
				'1': x,
				'2': str(encrypt(x, json.dumps(leader).encode('utf8')))
			}
		}


# Коды операций
# 1 - добавить/изменить элемент(-ы) [время, код операции, имя базы, значения]
# 2 - удалить элемент [время, код операции, имя базы, ключ]
# stack - массив массивов [[время, код операции, данные1, данные2, ...], ...]


# Функции пользователей
@app.route('/add')
def add():
	# {
	# 	'login'
	# 	'password'
	# 	'database'
	# 	'values' {}
	# }
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		return {"status": "error", "type error": "json recognition"}

	# Проверка целостности запроса
	if 'login' not in r or 'password' not in r or 'values' not in r or \
			'database' not in r or type(r['login']) != str or type(r['password']) != str or \
			type(r['values']) != dict or r['database'] not in database:
		return {"status": "error", "type error": 'json is not full'}

	# аутентификация
	if r['login'] not in user_logins:
		return {"status": "error", "type error": "wrong login/password"}
	if r['password'] != user_logins[r['login']]:
		return {"status": "error", "type error": "wrong login/password"}

	stack.append([time.time(), 1, r['database'], r['values']])
	return {'status': 'ok'}


@app.route('/delete', methods=['POST'])
def delete():
	# {
	# 	'login'
	# 	'password'
	# 	'database'
	# 	'values' []
	# }
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		return {"status": "error", "type error": "json recognition"}

	# Проверка целостности запроса
	if 'login' not in r or 'password' not in r or 'values' not in r or \
			'database' not in r or type(r['login']) != str or type(r['password']) != str or \
			type(r['values']) != list or r['database'] not in database:
		return {"status": "error", "type error": 'json is not full'}

	# аутентификация
	if r['login'] not in user_logins:
		return {"status": "error", "type error": "wrong login/password"}
	if r['password'] != user_logins[r['login']]:
		return {"status": "error", "type error": "wrong login/password"}

	stack.append([time.time(), 2, r['database'], r['values']])
	return {'status': 'ok'}


@app.route('/data', methods=['POST'])
def data():
	# {
	# 	'login'
	# 	'password'
	# }
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		return {"status": "error", "type error": "json recognition"}

	# Проверка целостности запроса
	if 'login' not in r or 'password' not in r or type(r['login']) != str or type(r['password']) != str:
		return {"status": "error", "type error": 'json is not full'}

	# аутентификация
	if r['login'] not in user_logins:
		return {"status": "error", "type error": "wrong login/password"}
	if r['password'] != user_logins[r['login']]:
		return {"status": "error", "type error": "wrong login/password"}

	return database


# дополнительные функции
@app.route('/status', methods=['GET'])
def test():
	x = randint(0, 999)
	if leader == myip:
		return {
			'1': x,
			'2': str(encrypt(x, json.dumps({'status': 'leader'}).encode('utf8')))
		}
	else:
		return {
			'1': x,
			'2': str(encrypt(x, json.dumps({'status': 'follower', 'leader': leader}).encode('utf8')))
		}


def authentication(ip, my_login):
	global leader

	for i in range(10):
		j = {
			'login': my_login,
			'ip': myip
		}
		x = randint(0, 999)
		r = requests.post(f'https://{ip}/servers/auth', verify=False, json={
			'1': x,
			'2': str(encrypt(x, json.dumps(j).encode('utf8')))
		}).json()
		if r['status'] == 'ok':
			leader = ip
			break
		else:
			r = decrypt(r['leader']['1'], eval(r['leader']['2']))
			ip = r


if debug:
	@app.route('/debug', methods=['GET'])
	def debug():
		x = randint(0, 999)
		return {
			'1': x,
			'2': str(encrypt(x, json.dumps({
				'database': database,
				'server_ips': server_ips,
				'stack': stack,
				'leader': leader,
				'login': login,
				'myip': myip,
				'cycle_time': cycle_time,
				'last_time_elections': last_time_elections,
				'votes': votes,
				'debug': debug_dict
			}).encode('utf8')))
		}

# Запуск таймеров

# Обновление времени
set_time = Timer(3600.0, timeset.settimeyandex)
set_time.start()
timeset.settimeyandex()

# Таймер голосования
ballot = Timer(6 * cycle_time, vote)
ballot.start()

# Таймер лидера
leader_cycle = Timer(cycle_time, func_leader)

# стартующая функция
if not first:
	authentication(start_leader, login)

if __name__ == '__main__':
	app.run()
