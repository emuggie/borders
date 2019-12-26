import logging.config
import pworm as app

from flask import Flask, request, Response, abort

logging.config.fileConfig('logger.conf')
logger = logging.getLogger(__name__)
app = Flask(__name__)

app.lookup("./demo/routes")

local = app.getLocal()

@app.route('/')
@app.route('/<path:reqPath>')
def index(reqPath:str="/") :
    if reqPath == "favicon.ico" :
        abort(404)
        return
    local.request = request
    try :
        res = app.handle(reqPath)
    except app.PathNotFoundError :
        print("404")
        abort(404)
        return "404 not found"
    except  Exception as error:
         abort(500)
         raise(error)
    logger.info(res)
    return res or "Response Not found"
