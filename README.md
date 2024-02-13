# taskmaster

- Commande Reload : Victor TO TEST 
- SIGHUP launches reload_config_file using config_file_path, task_list as globals Victor
- Start Delay : Mehdi Comparer avec supervisor sleep
- Task Status : Mehdi
- Kill 
- Stop Delay
- exit code et retries

- The number of processes to start and keep running
- Whether to start this program at launch or not
- Whether the program should be restarted always, never, or on unexpected exits only
- Which return codes represent an "expected" exit status
- How long the program should be running after it’s started for it to be considered
"successfully started"
• How many times a restart should be attempted before aborting
• Which signal should be used to stop (i.e. exit gracefully) the program
• How long to wait after a graceful stop before killing the program
• Options to discard the program’s stdout/stderr or to redirect them to files
• Environment variables to set before launching the program
• A working directory to set before launching the program
• An umask to set before launching the program



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