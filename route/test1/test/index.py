from flask import request
import threading

def before(response = None) :
    print('before test')
    return

def handle(response = None) :
    print('handle test')
    return "done from index"

def after(response = None) :
    print('after test')
    return