from flask import request
import threading

def before(response = None) :
    print('before test1')
    return

def handle(response = None) :
    print('handle test1')
    return "test1"

def after(response = None) :
    print('after test1')
    return