import pworm as app

local = app.getLocal()

@app.handler(on=lambda:local.request.command == "POST")
def post() :
    print(local.request.form)
    return "OK"