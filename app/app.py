import os
import importlib.util
import threading
import inspect

BEFORE_FUNC = 'before'
HANDLE_FUNC = 'handle'
AFTER_FUNC = 'after'
MAX_DEPTH = 30
__threadScoped__ = threading.local()

basePath = ""
routeMap = {}

def setBasePath(path:str) : 
    global basePath
    basePath = path
    return

def lookup() :
    global basePath
    for root, dirs, files in os.walk(basePath) :
        for file in files :
            if file.endswith(".py") :
                filePath = os.path.join(root, file)
                loadModule(filePath)
    global routeMap
    print(routeMap)

def loadModule(filePath:str) : 
    global routeMap, basePath
    spec = importlib.util.spec_from_file_location("rest.endpoint", filePath)
    handler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(handler)
    requestPath = filePath.replace("/index.py","/").replace(".py","/").replace(basePath,"")
    routeMap[requestPath] = handler
    return

def route(path:str) :
    path = "/" if path.strip() == "" else path
    path = path if path.endswith("/") else path + "/"
    path = path if path.startswith("/") else "/" + path
    return chainModule(path)

def chainModule(module:str, depth:int = None, prev:any=None) : 
    global routeMap, MAX_DEPTH, BEFORE_FUNC, HANDLE_FUNC, AFTER_FUNC
    depth = 0 if depth == None else depth
    
    if depth >= len(module) or getattr(__threadScoped__,'depth',0) > MAX_DEPTH : 
        return prev
    __threadScoped__.depth = getattr(__threadScoped__,'depth',0) + 1

    subIdx = module[depth:].find("/") + depth + 1 if module[depth:].find("/") > -1 else len(module)
    nextModule = module[0:subIdx] if subIdx > -1 else module
    

    try :
        handler = routeMap.get(nextModule)
        #print('before',nextModule,  prev)
        if handler != None and callable(getattr(handler, BEFORE_FUNC)) :
            prev = getattr(handler, BEFORE_FUNC)(prev) or prev
            print('before',nextModule,  prev)
    except ImportError as ie:
        print(ie)
    except Exception as ce :
        print(ce)

    
    if subIdx == -1 or subIdx == len(module) :
        if handler != None and callable(getattr(handler, HANDLE_FUNC)) :
            prev = getattr(handler, HANDLE_FUNC)(prev) or prev
            print(HANDLE_FUNC,nextModule, prev)
    else :
        prev = chainModule(module, subIdx + 2, prev) or prev

    try :
        if handler != None and callable(getattr(handler, AFTER_FUNC)) :
            prev = getattr(handler, AFTER_FUNC)(prev) or prev
            
    except ImportError as ie:
        print(ie)
    except Exception as ce :
        print(ce)
    print('after',nextModule, prev)
    return prev

def next() :
    return