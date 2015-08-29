import os

def run(**args):
    print "[#] in environment modules."
    print str(os.environ)
    return str(os.environ)

run()
