# taskmaster
42 School Project

## Goals

- This project is about the recreation of Task management application like supervisord
- The taskmaster server loads a yaml configuration describing each Task (number of process, expected exit codes, command to execute, environnement variables, etc) and monitor the execution of each Task
- The taskmaster client provides a command line to interract with the server


## Usage

### Installation


#### Virtual Environment Setup

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Server

```shell
python  server/main.py -c <path_to_config_file> -p <server_port>
```

### Client

```shell
python client/main.py -p <server_port>
```


### Task Description

Yaml configuration :

```yaml
programs:

  ls:
    cmd: "/bin/ls -l"
    numprocs: 3
    umask: 022
    workingdir: /taskmaster
    autostart: true
    autorestart: unexpected
    exitcodes:
    - 0
    - 2
    startretries: 0
    starttime: 0
    stopsignal: TERM
    stoptime: 1
    stdout: /var/logs/ls.stdout
    stderr: /var/logs/ls.stderr
    env:
      STARTED_BY: taskmaster
      ANSWER: 42

  sleep:
    cmd: "/bin/sleep 3"
    numprocs: 1
    umask: 022
    workingdir: /taskmaster
    autostart: false
    autorestart: unexpected
    exitcodes:
    - 0
    startretries: 3
    starttime: 10
    stopsignal: USR1
    stoptime: 3
    stdout: /var/logs/sleep.stdout
    stderr: /var/logs/sleep.stderr
    env:
      STARTED_BY: taskmaster
      ANSWER: 42
```

#### Program parameters

- `cmd` : Command to execute
- `numprocs` : Number of process to start
- `umask` : Umask to apply to the process
- `workingdir` : Working directory for the process
- `autostart` : Start the process at the launch of the server
- `autorestart` : 
  - `unexpected` : Restart the process if it exits with an unexpected exit code
  - `true` : Restart the process if it exits
  - `false` : Never restart the process
- `exitcodes` : List of expected exit codes
- `startretries` : Number of retries before considering the program as `ABORTED`
- `starttime` : Time to wait before considering the program as `RUNNING`
- `stopsignal` : Signal to send to the process to stop it
- `stoptime` : Time to wait after sending the stop signal before killing the process
- `stdout` : Path to the stdout log file
- `stderr` : Path to the stderr log file
- `env` : Environment variables to set for the process


### Client commands

- `start` <program>
- `stop` <program>
- `restart` <program>
- `reload`
- `status`
- `exit`

### Features

#### Mandatory

- Multiple process management
- Start / Stop / Restart
- Restart on unexpected exit code
- Status
- Running Time monitoring
- Task Reload (SIGHUP + reload command)
- Umask
- Working directory
- Retries
- Exit codes
- Autostart
- Autorestart
- Environment variables
- Log file management
- Stop signal
- Stop time


#### Bonus

- Client / Server architecture
- Mail alerting on Aborted / Unexpected exit
- Advanced Logging (levels + file)



### Send a SIGHUP signal to the server

```shell
(.venv) ➜  taskmaster git:(feat/sighup) ✗ ps -a
  PID TTY           TIME CMD
89039 ttys005    0:00.95 /usr/local/bin/zsh -il
90895 ttys005    0:00.13 /usr/local/Cellar/python@3.11/3.11.6_1/Frameworks/Python.framework/Versions/3.11/Resources/Python.a
89210 ttys011    0:00.73 /usr/local/bin/zsh
90947 ttys015    0:00.71 /usr/local/bin/zsh -il
91446 ttys015    0:00.01 ps -a
(.venv) ➜  taskmaster git:(feat/sighup) ✗ kill -HUP 90895
(.venv) ➜  taskmaster git:(feat/sighup) ✗ 
```


### Mail Alerting

The server can send mail alerts on the following events :
- Program Aborted
- Unexpected exit

#### Mail configuration with gmail address using SSL

- SMTP Sever : smtp.gmail.com
- Port : 465
- Username : Sender mail address
- Password : Gmail requires an App Password to be created (16 characters) in order to send mails from an application
- Dests : Comma-separated list of mail addresses


#### App Password Creation

Using a gmail account, you need to create an App Password in order to send mail from an application  

1) App password creation is under the 2-Step Verification menu (https://myaccount.google.com/signinoptions/two-step-verification)
2) At the bottom of the page there is an `App Passwords` submenu (https://myaccount.google.com/apppasswords)
3) Create an App Password and copy the password
