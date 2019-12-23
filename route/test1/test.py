from borders import handler, proceed

@handler()
def before(response = None) :
    print('before test')
    return proceed()

@handler()
def handle(response = None) :
    print('handle test')
    return proceed()

@handler()
def after(response = None) :
    print('after test')
    return proceed()