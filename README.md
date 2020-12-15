# GRUB

Simple and lightweight RAFT algorithm. Designed for connecting small databases on a large number of servers.

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

      $ sudo docker pull k0per/grub:alpine
  
- Ubuntu container:

      $ sudo docker pull k0per/grub:ubuntu
  
#### 3. First start
Run the command:

    $ sudo docker run -i -v /path/to/the/data/folder:/app/output -p 80:80 -p 443:443 --name grub k0per/grub:alpine
    
Command arguments explanation: 
    
* -i                                        — gives control of terminal to docker
* -v /path/to/the/data/folder:/app/output   — mounts the host directory to the container directory
* --name grub                               — gives the name "grub" to the container
* -p 80:80 -p 443:443                       — associates host port with the container's port
* k0per/grub:alpine (k0per/grub:ubuntu)     — target image (alpine or ubuntu) 
    
#### 4. Using
Start command:

    $ sudo docker start grub
    
Stop command: 

    $ sudo docker stop grub

Delete command (the data in the folder specified at the first start remains): 

    $ sudo docker rm grub

### Installation without using docker

#### 1. Download files: 

    $ git pull https://github.com/k0perX-X/GRUB.git

#### 2. Installing python packages
Run command: 

    $ sudo pip3 install flask requests pycryptodome   

#### 3. Setting up
Copy output/encrypt keys.py from another server or generate a new one with output/encrypt_keys_generator.py.

#### 4. Using
Run commands: 

    $ export FLASK_APP=app.py 
    $ flask run


  