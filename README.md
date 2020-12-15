# GRUB

Simple and lightweight RAFT algorithm. Designed for connecting small databases on a large number of servers.

## How to install 
There are two ways to install:
  1. Download and run docker image (recommended)
  2. Download the git and run it with flask
 
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
    
* -i - gives control of terminal to docker
* -v /path/to/the/data/folder:/app/output - mounts the host directory to the container directory
* --name grub - gives the name "grub" to the container
* -p 80:80 -p 443:443 - associates host port with the container's port
* k0per/grub:alpine (ubuntu) - target image (alpine or ubuntu) 
    
#### 4. Using
Start command:

    $ sudo docker start grub
    
Stop command: 

    $ sudo docker stop grub

Delete command (the data in the folder specified at the first start remains): 

    $ sudo docker rm grub

