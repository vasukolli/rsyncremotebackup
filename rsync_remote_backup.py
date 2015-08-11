__author__ = 'vasu'

from datetime import datetime
import sys, os, subprocess, tarfile, smtplib, re
import configparser, shutil
rsyncfailure = False
errormap = {}
curr_year = datetime.now().strftime('%Y')
curr_month = datetime.now().strftime('%B')
curr_date = datetime.now().strftime('%d')
curr_day = datetime.now().strftime('%A')
curr_time = datetime.now().strftime(('%H-%M-%S-%p'))
def print_usage(script):
    print('Usage:', script, '--hostlist <host configuration file>' , '--todir <directory>')
    sys.exit(1)

def usage(args):
    if not len(args) == 5:
        print_usage(args[0])
    else:
        req_args = ['--hostlist','--todir']
        for a in req_args:
            if not a in req_args:
                print_usage()
            if not os.path.exists(args[args.index(a)+1]):
                print('Error: Path not found:', args[args.index(a)+1])
                print_usage()
    hconf=args[args.index('--hostlist')+1]
    dir = args[args.index('--todir')+1]
    return hconf, dir

def create_host_directories(dir, section, ip):
    #Config = configparser.ConfigParser()
    #Config.read(hconf)
    #for section in Config.sections():
    if curr_date == "01":
        path = dir+"/"+section+'-'+ip+"/"+curr_year+"/"+"monthly"+"/"+curr_month+"/"+curr_date+"/"+curr_time
    elif curr_day == 'Sunday':
         path = dir+"/"+section+'-'+ip+"/"+curr_year+"/"+"weekly"+"/"+curr_month+"/"+curr_date+"/"+curr_time
    else:
         path = dir+"/"+section+'-'+ip+"/"+curr_year+"/"+"Daily"+"/"+curr_month+"/"+curr_date
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
    return path


def rsync_data(hconf, dir):
    Config = configparser.ConfigParser()
    Config.read(hconf)
    for section in Config.sections():
        backupdirs = Config.get(section, 'backupdirs').split(',')
        path = create_host_directories(dir, section, Config.get(section, 'ipaddress'))
        if not len(backupdirs)==0:
            for bakdirs in backupdirs:
                cmd=['rsync','-ahvz','--delete', Config.get(section, 'username')+'@'+Config.get(section, 'ipaddress')+':'+bakdirs, path]
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                if p.returncode > 0:
                    global rsyncfailure, errormap
                    rsyncfailure = True
                    if not Config.get(section, 'ipaddress') in errormap:
                        errormap[Config.get(section, 'ipaddress')] = stderr.decode(encoding='UTF-8')
                    else:
                        errormap[Config.get(section, 'ipaddress')] = str(errormap[Config.get(section, 'ipaddress')]) + stderr.decode(encoding='UTF-8')
                    continue
                else:
                    if curr_date == "01" or curr_day == "Sunday":
                        backup_compress(path, bakdirs)


def backup_compress(dir, bfile):
  print((bfile.replace("~",'')).rsplit('/',1)[1])
  bfile=str((bfile.replace("~",'')).rsplit('/',1)[1])
  dir = dir+'/'+bfile
  tar = tarfile.open(dir+'.tar.gz', 'w:gz')
  tar.add(dir, arcname=bfile)
  tar.close()
  shutil.rmtree(dir)


def sendmail(data):
    pattern = r"((([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])[ (\[]?(\.|dot)[ )\]]?){3}([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))"
    fromaddr="vasavakrishna@greenbuds.co.in"
    toaddr=["vasavakrishna@greenbuds.co.in"]
    header = 'From: %s\n' % fromaddr
    header += 'To: %s\n' % ','.join(toaddr)
    subject = 'Backup  Intimation'
  # header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    #cmd = ['hostname', '-I']
    #p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #stout, stderr = p.communicate()
    #iplist = ipaddress
    #ips = [match[0] for match in re.findall(pattern, iplist)]
    errmsg = data
    text="Backup Status"+'\n'+'Error Message : '+data
    message = header + text
    server = smtplib.SMTP('smtp.yourdomain.co:25')
    server.starttls()
    server.login("username@domain.com", "password")
    server.sendmail(fromaddr, toaddr, message)


def status_mail():
    if rsyncfailure:
        sendmail(str(errormap))
    else:
        sendmail('Rsynsing done successfully')



def main():
    hconf, dir = usage(sys.argv)
    #create_host_directories(hconf, dir)
    rsync_data(hconf,dir)
    status_mail()

if __name__ == '__main__':
    main()
