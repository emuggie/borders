from flask import request
import threading

def before(response = None) :
    print('before root', request.method)
    return

def handle(response = None) :
    print('handle root')
    return "/"

def after(response = None) :
    print('after root')
    return