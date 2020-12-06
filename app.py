import os.path

if not os.path.exists('output/encrypt_keys_generator.py'):
	print("""БЛЯТЬ ПИЗДЕЦ""")
	exit()


if not os.path.exists('output/encrypt_keys.py'):
	print("""The file output/encrypt keys.py is missing.
If this is your first server on the network, generate a file using output/encrypt_keys_generator.py.
If this is not your first server on the network, then copy the file from your other server.""")
	exit()

from flask import Flask, request
import json
import logging
import time
import requests
import traceback
from crypt import decrypt, encrypt
from output.config import login, first, start_leader, debug, base_cycle_time, multiplier_update_cycle_time, admin_logins
from output.user_logins import saved_user_logins
from output.database import saved_database
from random import randint, choice
import timeset
from threading import Timer, Thread
import urllib3

urllib3.disable_warnings()  # отключает уведомление о не верифицированном ssl

# data
stack = []
leader = ''
server_ips = {
	login: requests.get('https://api.ipify.org?format=json').json()['ip']
}
database = saved_database
user_logins = saved_user_logins
myip = requests.get('https://api.ipify.org?format=json').json()['ip']
cycle_time = base_cycle_time
last_time_elections = time.time()
votes = {}
if debug:
	debug_dict = {}
response_time = {}
lost_leader = {}

app = Flask(__name__)
logging.basicConfig(filename="output/log.txt", level=logging.WARNING)


# Функции голосования
def vote():
	global last_time_elections
	global ballot
	global leader
	global votes
	global cycle_time
	global leader_cycle
	global update_cycle_time
	global lost_leader

	def send_vote(ip, x):
		nonlocal res
		try:
			r = requests.post(f"https://{ip}/servers/votes", verify=False, json={
				'1': x,
				'2': str(encrypt(x, json.dumps(j).encode('utf8')))
			})
			r.json()
			res.append(r)
		except:
			if 'r' in locals():
				logging.error(f'vote - {ip} - json - {r} \n {traceback.format_exc()}')
			else:
				logging.error(f'vote - {ip} \n {traceback.format_exc()}')

	def vote_new_leader(ip, x):
		nonlocal res
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
				if 'r' in locals():
					logging.error(f'vote - new_leader - localhost - {ip} - json - {r}\n {traceback.format_exc()}')
				else:
					logging.error(f'vote - new_leader - localhost - {ip}\n {traceback.format_exc()}')
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
				if 'r' in locals():
					logging.error(f'vote - new_leader - localhost - {ip} - json - {r}\n {traceback.format_exc()}')
				else:
					logging.error(f'vote - new_leader - localhost - {ip}\n {traceback.format_exc()}')

	# рассылка голоса
	my_vote = choice([*server_ips.values()])
	j = {
		'ip': myip,
		'vote': my_vote
	}
	res = []
	for ip in server_ips.values():
		if ip != myip:
			x = randint(0, 999)
			p = Thread(target=send_vote, args=(ip, x))
			p.start()

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
		return

	# подведение результатов
	if max_ip[0] == myip:

		# если выбрали меня
		res = []
		for ip in server_ips.values():
			x = randint(0, 999)
			p = Thread(target=vote_new_leader, args=(ip, x))
			p.start()

		time.sleep(3 * cycle_time)
		# запуск циклов
		leader_cycle.cancel()
		leader_cycle = Timer(cycle_time, func_leader)
		leader_cycle.start()
		ballot.cancel()
		ballot = Timer(6 * cycle_time, vote)
		ballot.start()
		cycle_time = base_cycle_time
		update_cycle_time.cancel()
		update_cycle_time = Timer(cycle_time * multiplier_update_cycle_time, func_update_cycle_time)
		update_cycle_time.start()

	else:
		# если выбрали не меня
		time.sleep(3 * cycle_time)
		if time.time() - 4 * cycle_time >= last_time_elections:
			vote()
			return
		else:
			last_time_elections = time.time()
			ballot.cancel()
			ballot = Timer(6 * cycle_time, vote)
			ballot.start()
	lost_leader = {}


@app.route('/servers/new_leader', methods=['POST'])
def new_leader():
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		logging.error(time.ctime(time.time()) + f"new_leader - json recognition - not json - json - {request.data}")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	# encrypt
	try:
		r = decrypt(r['1'], eval(r['2']))
	except Exception as e:
		logging.error(time.ctime(time.time()) + f"new_leader - json recognition - encode - json - {r}")
		return {"status": "error", "type error": "json recognition", "json recognition": "encode"}

	# преобразование json запроса
	try:
		r = json.loads(r)
	except Exception as e:
		logging.error(time.ctime(time.time()) + f"new_leader - json recognition - not json - json - {r}")
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
		logging.error(time.ctime(time.time()) + f"func_votes - json recognition - not json - json - {request.data}")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	# encrypt
	try:
		r = decrypt(r['1'], eval(r['2']))
	except Exception as e:
		logging.warning(time.ctime(time.time()) + f"func_votes - json recognition - encode- json - {r}")
		return {"status": "error", "type error": "json recognition", "json recognition": "encode"}

	# преобразование json запроса
	try:
		r = json.loads(r)
	except Exception as e:
		logging.warning(time.ctime(time.time()) + f"func_votes - json recognition - not json - json - {r}")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	if time.time() - 3 * cycle_time < last_time_elections:
		return {'status': 'leader', 'leader': leader}
	if r['ip'] not in lost_leader:
		lost_leader[r['ip']] = 1
	else:
		lost_leader[r['ip']] += 1
	if lost_leader[r['ip']] > 5:
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
	global response_time
	global user_logins

	def leader_request(ip, x):
		nonlocal res

		excepttf = False
		start_time = time.time()
		if ip == myip:
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
			try:
				r = requests.post(f"https://{ip}/servers/follower", verify=False, json={
					'1': x,
					'2': str(encrypt(x, json.dumps(j).encode('utf8')))
				})
				r.json()
				r = decrypt(r['1'], eval(r['2']))
				r = json.loads(r)
				res += r
				global ballot
				ballot.cancel()
				ballot = Timer(6 * cycle_time, vote)
				ballot.start()
			except:
				excepttf = True
				if 'r' in locals():
					logging.warning(f'leader - {ip} - json - {r}\n {traceback.format_exc()}')
				else:
					logging.warning(f'leader - {ip}\n {traceback.format_exc()}')
		if not excepttf:
			if ip in response_time:
				if type(response_time) != str:
					if response_time[ip] < time.time() - start_time:
						response_time[ip] = time.time() - start_time
					else:
						pass
				else:
					response_time[ip] = time.time() - start_time
			else:
				response_time[ip] = time.time() - start_time
		else:
			response_time[ip] = 'except'

	# Создаём запрос
	j = {
		'ip': myip,
		'data': {
			'database': database,
			'server_ips': server_ips,
			'cycle_time': cycle_time,
			'user_logins': user_logins
		}
	}
	res = []

	# рассылаем запрос всем
	p = []
	for ip in server_ips.values():
		x = randint(0, 999)
		p.append(Thread(target=leader_request, args=(ip, x)))
		p[len(p) - 1].start()

	# Ожидаем когда все ответят
	tf = True
	ch = time.time()
	while tf:
		time.sleep(0.01)
		tf = False
		for i in p:
			if i.is_alive():
				tf = True
		if time.time() - ch > cycle_time:  # если слишком долго
			tf = False

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
		elif deystv[1] == 3:
			user_logins = {**user_logins, **deystv[2]}


# Функция фоловера
@app.route('/servers/follower', methods=['POST'])
def follower():
	global ballot
	global server_ips
	global cycle_time
	global stack

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
		if r['data']['cycle_time'] != cycle_time and myip != leader:
			cycle_time = r['data']['cycle_time']
			ballot.cancel()
			ballot = Timer(6 * cycle_time, vote)
			ballot.start()
		user_logins = r['data']['user_logins']
		new_stack = stack
		stack = []
		save_database()
		save_user_logins()
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
# 3 - добавить пользователя [время, код операции, {username, password}]
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
	if 'login' not in r or 'password' not in r or 'values' not in r or 'database' not in r:
		return {"status": "error", "type error": 'json is not full'}
	if type(r['login']) != str or type(r['password']) != str or type(r['values']) != dict:
		return {"status": "error", "type error": 'json is not full'}
	if r['database'] not in database:
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
	# 	'password' md5
	# 	'database'
	# 	'values' []
	# }
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		return {"status": "error", "type error": "json recognition"}

	# Проверка целостности запроса
	if 'login' not in r or 'password' not in r or 'values' not in r or 'database' not in r:
		return {"status": "error", "type error": 'json is not full'}
	if type(r['login']) != str or type(r['password']) != str or type(r['values']) != list or type(r['database']) != str:
		return {"status": "error", "type error": 'json is not full'}
	if r['database'] not in database:
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
	# 	'password' md5
	# }
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		return {"status": "error", "type error": "json recognition"}

	# Проверка целостности запроса
	if 'login' not in r or 'password' not in r:
		return {"status": "error", "type error": 'json is not full'}
	if type(r['login']) != str or type(r['password']) != str:
		return {"status": "error", "type error": 'json is not full'}

	# аутентификация
	if r['login'] not in user_logins:
		return {"status": "error", "type error": "wrong login/password"}
	if r['password'] != user_logins[r['login']]:
		return {"status": "error", "type error": "wrong login/password"}

	return database


@app.route('/add_user', methods=['POST'])
def add_user():
	# {
	# 	'login'
	# 	'password' md5
	# 	'user': {
	# 		'username'
	#		'password' md5
	# 	}
	# }
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		return {"status": "error", "type error": "json recognition"}

	# Проверка целостности запроса
	if 'login' not in r or 'password' not in r or 'user' not in r:
		return {"status": "error", "type error": 'json is not full'}
	if type(r['login']) != str or type(r['password']) != str or type(r['user']) != dict:
		return {"status": "error", "type error": 'json is not full'}
	if 'username' not in r['user'] or 'password' not in r['user']:
		return {"status": "error", "type error": 'json is not full'}
	if type(r['user']['username']) != str or type(r['user']['password']) != str:
		return {"status": "error", "type error": 'json is not full'}

	# аутентификация
	if r['login'] not in admin_logins:
		return {"status": "error", "type error": "wrong login/password"}
	if r['password'] != user_logins[r['login']]:
		return {"status": "error", "type error": "wrong login/password"}

	stack.append([time.time(), 3, r['user']])
	return {'status': 'ok'}


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


def save_database():
	f = open('output/database.py', 'w')
	f.write('saved_database = ' + str(database))
	f.close()


def save_user_logins():
	f = open('output/user_logins.py', 'w')
	f.write("from hashlib import md5\n# 'username': md5('password'.encode('utf8')).hexdigest()\n\nsaved_user_logins = " + str(user_logins))
	f.close()


def func_update_cycle_time():
	global ballot
	global leader_cycle
	global update_cycle_time
	global cycle_time
	global response_time
	r = 0
	for i in response_time.values():
		if type(i) == float:
			if i > r:
				r = i
	response_time = {}
	if r != 0:
		cycle_time = r * 2
		if leader == myip:
			leader_cycle.cancel()
			leader_cycle = Timer(cycle_time, func_leader)
			leader_cycle.start()
			ballot.cancel()
			ballot = Timer(6 * cycle_time, vote)
			ballot.start()
			update_cycle_time.cancel()
			update_cycle_time = Timer(cycle_time * multiplier_update_cycle_time, func_update_cycle_time)
			update_cycle_time.start()


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

# Таймер обновления cycle_time
update_cycle_time = Timer(cycle_time * multiplier_update_cycle_time, func_update_cycle_time)


# стартующая функция
if not first:
	authentication(start_leader, login)

if __name__ == '__main__':
	app.run()
