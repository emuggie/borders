import borders as app

@app.handler()
def before(response = None) :
    print('before test')
    return app.proceed()

@app.handler()
def handle(response = None) :
    print('handle test')
    return app.proceed()

@app.handler()
def after(response = None) :
    print('after test')
    return app.proceed()