# [UPM] Universal Package Manager


## The Repo

This repo contains all you need to install UPM or contribute to the project

**The folder `ftp.upm.org` is the local path for the FTP Server, you can just ignore it or host it with FileZilla or similiar FTP Hosting Softwares**



## Usage

### Package Installation
*Local source* 
```json
python ./src/upm.py get helloworld>=1.5
```
*with PATH*
```json
upm get helloworld>=1.5
```


## Requirements

  - Python3.X.X
  - `python-dotenv` __(setup/req.txt)__
  
## Setup

__Linux:__

After the first execution add `~/.upm/bin/` to the PATH



__Windows:__

Auto-setup on first execution
