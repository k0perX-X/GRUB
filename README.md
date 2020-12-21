# GRUB

Simple and lightweight RAFT algorithm. Designed for connecting small databases on a large number of servers.

## Table of contents

1. [How to install](#How-to-install)
   1. [Installation using docker](#Installation-using-docker)
   2. [Installation without using docker](#Installation-without-using-docker)
2. [How to use](#How-to-use)
    1. [Types of requests](#Types-of-requests)
    2. [User requests](#User-requests)
       1. [Query data from the database](#Query-data-from-the-database)
       2. [Database add query](#Database-add-query)
       3. [Request to delete data from the database](#Request-to-delete-data-from-the-database)
       4. [Request to add a new user](#Request-to-add-a-new-user)
    3. [System requests](#System-requests)

## How to install 
There are two ways to install:
  1. Installation using docker (recommended)
  2. Installation without using docker
 
### Installation using docker

#### 1. Install docker

Follow the instructions from the official website: https://docs.docker.com/engine/install/

#### 2. Download image

Download image using the command:

- Alpine container (recommended):
  
    ```shell
    $ sudo docker pull k0per/grub:alpine
    ```
  
- Ubuntu container:
  
    ```shell
    $ sudo docker pull k0per/grub:ubuntu
    ```
  
#### 3. First start

Run the command:

```shell
$ sudo docker run -i -v /path/to/the/data/folder:/app/output -p 80:80 -p 443:443 --name grub k0per/grub:alpine
```

Command arguments explanation: 

```
-i                                        — gives control of terminal to docker
-v /path/to/the/data/folder:/app/output   — mounts the host directory to the container directory
--name grub                               — gives the name "grub" to the container
-p 80:80 -p 443:443                       — associates host port with the container's port
k0per/grub:alpine (k0per/grub:ubuntu)     — target image (alpine or ubuntu) 
``` 

#### 4. Using

Start command:

```shell
$ sudo docker start grub
```

Stop command:

```shell
$ sudo docker stop grub
```

Delete command (the data in the folder specified at the first start will be saved): 

```shell
$ sudo docker rm grub
```

### Installation without using docker

#### 1. Download files

Run command: 

```shell
$ git pull https://github.com/k0perX-X/GRUB.git
```

#### 2. Installing python packages

Run command: 

```shell
$ sudo pip3 install flask requests pycryptodome   
```

#### 3. Setting up

Copy output/encrypt keys.py from another server or generate a new one with output/encrypt_keys_generator.py.

#### 4. Using

Run commands: 

```shell
$ export FLASK_APP=app.py 
$ flask run
```

## How to use

All communications with servers are carried out via json POST requests. 

When sending requests over a local network, it is recommended to use the http protocol. 
For requests outside the local network, the https protocol should be used without ssl 
key verification.

### Types of requests

1. User requests:
    * query data from the database
    * database add query
    * request to delete data from the database
    * request to add a new user
2. System requests:
    * status request
    * debug request

User requests use a user authorization system, System requests use a data encryption system.

### User requests

All json requests contain "login" and "password". The password is transmitted in md5 hash format (utf32).

#### Query data from the database

POST request to address: `https://ip(url)/data`

Request:

```json
{
    "login": "username",
    "password": "md5 hash password"
}
```

Answer: 

```json
{
    "name of databese1": 
    {
        "key1": "value1",
        "key2": "value2",
        ...
    },
    "name of databese2":
    {
        "key1": "value1",
        "key2": "value2",
        ...
    }
}
```

#### Database add query
POST request to address: `https://ip(url)/add`

Request:

```json
{
    "login": "username",
    "password": "md5 hash password",
    "database": "name of databese",
    "values":
    {
        "key1": "value1",
        "key2": "value2",
        ...
    }
}
```

Answers: 

```json
{"status": "error", "type error": "json is not full"}
{"status": "error", "type error": "unknown database"}
{"status": "error", "type error": "wrong login/password"}
{"status": "ok"}
```

#### Request to delete data from the database

POST request to address: `https://ip(url)/delete`

Request:

```json
{
    "login": "username",
    "password": "md5 hash password",
    "database": "name of databese",
    "values":
    [
        "key1",
        "key2",
        ...
    ]
}
```

Answers: 

```json
{"status": "error", "type error": "json is not full"}
{"status": "error", "type error": "unknown database"}
{"status": "error", "type error": "wrong login/password"}
{"status": "ok"}
```

#### Request to add a new user

To complete the request, the user must be in admin_logins.

POST request to address: `https://ip(url)/add_user`

Request:

```json
{
    "login": "username",
    "password": "md5 hash password",
    "user": 
    {
        "login": "username",
        "password": "md5 hash password"
    }
}
```

Answers: 

```json
{"status": "error", "type error": "json is not full"}
{"status": "error", "type error": "unknown database"}
{"status": "error", "type error": "user not admin"}
{"status": "error", "type error": "wrong login/password"}
{"status": "ok"}
```

### System requests

System requests require the use of crypt.py and output/encrypt keys.py. 
output/encrypt keys.py must match the file on the target server. 
Usage example:

#### Status request

```python
import crypt, requests, json
status = requests.get(f'https://{ip}/status')
status = status.json()
status = crypt.decrypt(status['1'], status['2'])
status = json.loads(status)
```

#### Debug request

```python
import crypt, requests, json
debug = requests.get(f'http://{ip}/debug')
debug = debug.json()
debug = crypt.decrypt(debug['1'], debug['2'])
debug = json.loads(debug)
```
