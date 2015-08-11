# rsyncremotebackup
python rsync script to backup multiple remote hosts to local machine.


Sample usage:
python3 rsyncremotebackup.py --hostlist hostlist.cnf --todir /dump_location

Requirements:
a) python version 3.x
b) passwordless authentication should be configured between two servers.
