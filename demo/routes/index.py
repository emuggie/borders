import threading
import json
from logging import getLogger
import pworm as app

logger = getLogger(__name__)

local = app.getLocal()

@app.handler(on=app.isExactPath)
def get() :
    appInfo = { "modules" : list(app.modules.keys()) }
    return json.dumps(appInfo)

