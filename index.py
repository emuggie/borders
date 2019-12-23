import logging.config
import importlib
import threading
import borders

from flask import Flask, request, Response,abort

logging.config.fileConfig('logger.conf')
logger = logging.getLogger(__name__)
logger.debug("Start %s" , __name__)
app = Flask(__name__)

borders.setBasePath("./route")
borders.lookup()

local = borders.getLocal()

@app.route('/')
@app.route('/<path:reqPath>')
def index(reqPath:str="/") :
    if reqPath == "favicon.ico" :
        abort(404)
        return
    local.request = request
    try :
        res = borders.handle(reqPath)
    except borders.PathNotFoundError :
        print("404")
        abort(404)
        return "404 not found"
    # except  Exception as error:
    #     print("500", error)
    #     abort(500)
    #     raise(error)
    print(res)
    return res or "Response Not found"
