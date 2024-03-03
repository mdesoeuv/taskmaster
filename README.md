# taskmaster
42 School Project

## Goals

- This project is about the recreation of Task management application like supervisord
- The taskmaster server loads a yaml configuration describing each Task (number of process, expected exit codes, command to execute, environnement variables, etc) and monitor the execution of each Task
- The taskmaster client provides a command line to interract with the server


### Task Description

Yaml configuration :

```
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


### Client commands

- `start` <program>
- `stop` <program>
- `reload`
- `status`

### Features

- Task Reload
- Restart on unexpected exit code
- Running Time monitoring


### Launch sighup

(.venv) ➜  taskmaster git:(feat/sighup) ✗ ps -a
  PID TTY           TIME CMD
89039 ttys005    0:00.95 /usr/local/bin/zsh -il
90895 ttys005    0:00.13 /usr/local/Cellar/python@3.11/3.11.6_1/Frameworks/Python.framework/Versions/3.11/Resources/Python.a
89210 ttys011    0:00.73 /usr/local/bin/zsh
90947 ttys015    0:00.71 /usr/local/bin/zsh -il
91446 ttys015    0:00.01 ps -a
(.venv) ➜  taskmaster git:(feat/sighup) ✗ kill -HUP 90895
(.venv) ➜  taskmaster git:(feat/sighup) ✗ 


### Mail Alerting

#### Mail configuration with gmail address using SSL

- SMTP Sever : smtp.gmail.com
- Port : 465
- Username : Sender mail address
- Password : Gmail requires an App Password to be created (16 characters) in order to send mails from an application
- Dests : Comma-separated list of mail addresses
- 

#### App Password Creation

1) App password creation is under the 2-Step Verification menu (https://myaccount.google.com/signinoptions/two-step-verification)
2) At the bottom of the page there is an `App Passwords` submenu (https://myaccount.google.com/apppasswords)
3) Create an App Password and copy the password
