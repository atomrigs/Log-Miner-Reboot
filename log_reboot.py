#!/usr/bin/env python
import socket
import sys, os
import shutil
from datetime import datetime
import subprocess
import re

log_file_name = 'noappend.log'
now = str(datetime.now())
if sys.platform == 'win32':
  log_loc = 'Q:/log_reboot/'
  #log_loc = ''
else:
  log_loc = '/share/log_reboot/'
group = 'a'

def get_myip():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(('8.8.8.8', 0))
  return s.getsockname()[0]

def get_failed_gpus(log_file_name):
  pattern = "WATCHDOG: GPU (.*) hangs in OpenCL call, exit"
  log = open(log_file_name,'r').read()
  result = re.findall(pattern, log)
  return list(set(result))

def save_log_file(worker_name, failed_gpus):
  with open(log_loc + worker_name + '.txt', 'a') as log_event:
    log_event.write("\n\r" + now + " Failed GPUs: " + str(failed_gpus))
    
  if not os.path.exists(log_loc + worker_name):
    os.makedirs(log_loc + worker_name)
    
  if os.path.exists(log_file_name):
    if sys.platform == 'win32':
      data = subprocess.check_output("powershell gc -TotalCount 50 %s" % log_file_name, shell=True)
      data += subprocess.check_output("powershell gc -Tail 50 %s" % log_file_name, shell=True)
    else:
      data = subprocess.check_output("head -50 %s" % log_file_name, shell=True)
      data += subprocess.check_output("tail -50 %s" % log_file_name, shell=True)
    with open(log_loc + worker_name + '/'+ now.replace(' ', '-').replace(':','-')[:16] + '.log', 'w') as log:
      log.write(data)
      
  print "Finished logging..."
	  
def main():
  worker_name = group + '-' + get_myip()
  failed_gpus = get_failed_gpus(log_file_name)
  save_log_file(worker_name, failed_gpus)


if __name__ == "__main__":
   main()  

