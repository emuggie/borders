import importlib
import threading
import app.app as rt

from flask import Flask, request
app = Flask(__name__)

rt.setBasePath("./route")
rt.lookup()

@app.route('/')
@app.route('/<path:reqPath>')
def index(reqPath:str="/") :
    res = rt.route(reqPath)
    return res




