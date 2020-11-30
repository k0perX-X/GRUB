from flask import Flask, request
import json
import logging
import time
import requests
import traceback
from crypt import decrypt, encrypt
from random import randint, choice
from hashlib import md5
import timeset
from threading import Timer


# data
stack = []
leader = ''
server_ips = {}
database = {

}
user_logins = {

}
myip = requests.get('https://api.ipify.org?format=json').json()['ip']
cycle_time = 1
last_time_elections = time.time()
votes = {}


app = Flask(__name__)
logging.basicConfig(filename="log.txt", level=logging.WARNING)


# Функции голсования
def vote():
	# рассылка голоса
	my_vote = choice(server_ips.values())
	j = {
		'ip': myip,
		'vote': my_vote
	}
	res = []
	for ip in server_ips.values():
		x = randint(0, 999)
		try:
			r = requests.post(f"https://{ip}/servers/votes", verify=False, json={
				'1': x,
				'2': str(encrypt(x, json.dumps(j).encode('utf8')))
			}).json()
			res.append(r)
		except:
			pass

	# проверка на ошибку голосования
	for i in res:
		if i['status'] == 'leader':
			global leader
			leader = i['leader']
			# зупустить новый таймер выборов
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
		for ip in server_ips.values():
			x = randint(0, 999)
			try:
				r = requests.post(f"https://{ip}/servers/new_leader", verify=False, json={
					'1': x,
					'2': str(encrypt(x, json.dumps({
						'status': 'ok',
						'ip': myip
					}).encode('utf8')))
				}).json()
				res.append(r)
			except:
				pass
		time.sleep(3 * cycle_time)
		# запуск циклов

	else:
		# если выбрали не меня
		time.sleep(3 * cycle_time)
		if time.time() - 4 * cycle_time >= last_time_elections:
			vote()
		else:
			global last_time_elections
			last_time_elections = time.time()
			# запуск таймера на выборы


@app.route('/servers/new_leader', methods=['POST'])
def new_leader():
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "votes - json recognition - not json")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	# encrypt
	try:
		r = decrypt(r['1'], eval(r['2']))
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "votes - json recognition - encode")
		return {"status": "error", "type error": "json recognition", "json recognition": "encode"}

	# преобразование json запроса
	try:
		r = json.loads(r)
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "votes - json recognition - not json")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	global leader
	leader = r['ip']

	global last_time_elections
	last_time_elections = time.time()
	return {'status': 'ok'}


@app.route('/servers/votes', methods=['POST'])
def votes():
	# преобразование json запроса
	try:
		r = json.loads(request.data)
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "votes - json recognition - not json")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	# encrypt
	try:
		r = decrypt(r['1'], eval(r['2']))
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "votes - json recognition - encode")
		return {"status": "error", "type error": "json recognition", "json recognition": "encode"}

	# преобразование json запроса
	try:
		r = json.loads(r)
	except Exception as e:
		logging.warning(time.ctime(time.time()) + "votes - json recognition - not json")
		return {"status": "error", "type error": "json recognition", "json recognition": "not json"}

	if time.time() - 3 * cycle_time < last_time_elections:
		return {'status': 'leader', 'leader': leader}

	votes[r['ip']] = r['vote']
	return {'status': 'ok'}


@app.route('/test', methods=['GET'])
def test():
	return {'1': '1'}


# Коды операций
# 1 - добавить/изменить элемент(-ы)
# 2 - удалить элемент
# stack - массив масиивов [[время, код операции, данные1, данные2, ...], ...]


# Запуск таймеров

# Обновление времени
t = Timer(3600.0, timeset.settimeyandex)
t.start()
timeset.settimeyandex()

# Таймер голосования
t = Timer(6 * cycle_time, vote)


if __name__ == '__main__':
	app.run()
