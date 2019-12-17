import importlib
import threading
import serverlease
import serverlease.loader

from flask import Flask, request, Response,abort
app = Flask(__name__)

serverlease.setBasePath("./route")
serverlease.lookup()

@app.route('/')
@app.route('/<path:reqPath>')
def index(reqPath:str="/") :
    if reqPath == "favicon.ico" :
        abort(404)
        return
    res = serverlease.route(reqPath)
    return res
