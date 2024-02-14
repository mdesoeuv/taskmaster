# taskmaster

- Commande Reload : OK
- SIGHUP : OK
- Start Delay : changer en starttime validation selon le sujet
- Task Status : Mehdi : OK -> valider
- Kill : OK -> valider en testant differents signals
- Stop Delay : changer en timeout de thread join apres avoir envoye le signal specifie
- exit code et retries : Mehdi : OK -> valider
- Ajouter un handler de type file pour le logger (doit logguer les actions du programme)
- Ajouter un historique dans la ligne de commande : Victor
- Etude de supervisord -> Verifier le comportement des toutes les commandes du sujet
- 
- Valider le comportement du restart vis a vis des retries and l'implementer (remettre les valeurs a 0 lors du restart) : Victor
- Tester le CWD : Mehdi
- Gestion de l'ecriture dans la console avec le multi-threading : Victor
- Mise en forme de la verbose avec un niveau INFO correspondant a supervisord : Victor
- Reload sans tuer les process si les parametres critiques sont constants ou qu'il s'agit d'augmenter le nombre de process
- Valider le umask + documenter : Mehdi
- Interpreter le stopsignal "USR1" de la config exemple du sujet
- Gestion des parametres d'autorestart "unexpected, always, never" : Mehdi
- Documentation 
- Preparer des configs exemples diversifiee
- Crash tests
- Bonus
 
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


### Local SMTP Server

`python -m smtpd -c DebuggingServer -n localhost:1025`