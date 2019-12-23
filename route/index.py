import threading
import json
from logging import getLogger
import borders as app

logger = getLogger(__name__)

local = app.getLocal()

@app.handler()
def get() :
    print('get1',local.request.method, app.isExactPath(), app.getCurrentPath(), app.getRequestPath())
    return "index"

@app.handler(on = lambda : app.getRequestPath() == "tested/", block = False)
def get2() :
    print ('get2')
    return "test3"

