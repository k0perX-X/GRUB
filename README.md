# GRUB

## How to install 
There are two ways to install:
  1. Download and run docker image (recommended)
  2. Download the git and run it with flask
 
### Using docker

#### 1. Install docker
Follow the instructions from the official website: https://docs.docker.com/engine/install/

#### 2. Download image
Download image using the command:
  
    $ sudo docker pull k0per/grub
  
#### 3. Installation
Run the command:

    $ sudo docker run -i -p 80:80 -p 443:443 -v /path/to/the/data/folder:/app/output -t grub k0per/grub
    
Command arguments explanation: 
    
* -i - gives control of terminal to docker
* -p 80:80 -p 433:433 - associates host port with container's port
* -v /path/to/the/data/folder:/app/output - mounts the host directory to the container directory
* -t grub - gives the name "grub" to the container
    
