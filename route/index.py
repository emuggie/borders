from flask import request
import threading
import json

print("module loaded")

def before(*response) :
    print('before root', request.remote_addr)
    return

def handle(*response) :
    return json.dumps({"file":"/index.py"})

def after(*response) :
    print('after root')
    return