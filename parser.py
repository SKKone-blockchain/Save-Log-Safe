import re
import time
import schedule 
import os
import shutil

file_count = 0
oldsize = 0

# get updated log file with log_file and old_log_file
def get_updated_log(log_file, old_log_file, updated_log_file):
        
    file = open(log_file, "r")
    file2 = open(old_log_file, "r")
    
    updated_log = []
    
    while True:
        line = file.readline()
        line2 = file2.readline()
        
        if not line : break
                    
        # same log
        if line == line2 : continue

        # different log
        #line = file.readline()

        while line :
            line = line.replace("\n", "")
            updated_log.append(line)
            line = file.readline()
            
        break

        
    file.close()
    file2.close()
    
    return updated_log


def save_log():
    
    # log_file_path : /var/log/apache2/access.log
  
    log_file = "/var/log/apache2/access.log"
    old_log_file = "./old_log.txt"
    updated_log_file = "./updated_log.txt"

    regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+)+ (\d+) "(.*?)" "(.*?)"'
    
    global file_count
    global oldsize
    
    
    size = os.path.getsize(log_file)
    
    # if log file divided(per one day)   
    if oldsize > size:
        file_count += 1
        shutil.copyfile(old_log_file, 'old_log%d.txt' %file_count)
        shutil.copyfile(log_file, old_log_file)
        oldsize = size
        return
                                               
        
    oldsize = size
  
    
    # write updated log        
    updated_log = get_updated_log(log_file, old_log_file, updated_log_file)

    '''
    for i in updated_log:
        print(i)
    print(updated_log)	
    '''
    

    # write old log
    shutil.copyfile(log_file, old_log_file)

    return updated_log

        

def periodic_save():
    schedule.every(10).seconds.do(save_log)
    
    while True:
        schedule.run_pending()

if __name__ == "__main__":
    log_file = "/var/log/apache2/access.log"
    old_log_file = "./old_log.txt"
    
    shutil.copyfile(log_file, old_log_file)
    periodic_save()

def is_valid_log(log):
    
    regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+)+ (\d+) "(.*?)" "(.*?)"'
    
    p = re.compile(regex)

    if p.match(log):
        return True

    else:
        return False
