import os, inspect
from importlib.util import spec_from_file_location, module_from_spec
from typing import Any, Callable, Union

from .logging import getLogger
# Base import path of modules
basePath = None
modules = {}
moduleTree = {}

logger = getLogger(__name__)

def setBasePath(path:str) -> None : 
    """
    Set base directory for module location to lookup
    """
    global basePath
    # Error when tries to set base base multiple time
    if basePath != None :
        raise Exception('basePath already Initialized', basePath)
    # Raise error if basePath is invalid

    basePath = path if path.endswith("/") else path + "/"
    logger.debug("BasePath for Modules :", basePath)
    return

def lookup() -> None :
    """
    look for python files. 
    """
    global basePath, modules
    if basePath == None : 
        logger.debug("BasePath reconfigured to current path : ./")
    basePath = "./" if basePath == None else basePath
    for root, dirs, files in os.walk(basePath) :
        # Ignore hidden directories which starts with '__'
        if root.find("/__") > -1 :
            logger.debug("Directory ignored :",root)
            continue

        # Directory with empty handler
        modules.update({root.replace(basePath,""): None})

        for file in files :
            if not file.endswith(".py") :
                continue
            filePath = os.path.join(root, file)
            logger.debug("Module found : ", filePath)
            loadModule(filePath)
    # Print total routes
    logger.debug("Module loaded : ", modules)
    logger.debug("Module tree built : ", moduleTree)

# Load py file in filePath.
def loadModule(filePath:str, reload:bool = False) -> None : 
    global basePath, modules, moduleTree
    # Return if module already loaded by import
    if filePath in modules :
        return
    # Import hard way
    try :
        moduleName = __name__ + ".lookup." \
            + filePath.replace(basePath, "").replace("/",".").replace(" ","_").rstrip(".py")

        spec = spec_from_file_location(moduleName, filePath)
        module = module_from_spec(spec)
        modules.update({ filePath : module })
        spec.loader.exec_module(module)
        logger.debug("Module added : ", moduleName)
    except Exception as error : 
        raise(error)

# Add loaded Module to dict tree for route lookup
def addToTree(path:str, handler, treeNode:dict) -> None :
    childPath = path[:path.find("/")] if path.find("/")> -1 else path
    remainPath = path[path.find("/")+1:] if path.find("/")> -1 else None
    if remainPath == None or remainPath == "" :
        if childPath in treeNode :
            treeNode[childPath].append(handler)
        else :
            treeNode.update({ childPath : [handler] })
        return
    
    if not childPath in treeNode :
        treeNode.update({ childPath : {} })
        
    addToTree(remainPath, handler, treeNode.get(childPath))

class Handler :
    """
        Decorator class for handler function and  module.
    """
    def __init__(self, handlerFunc:Callable) :
        global modules,basePath
        self.handlerFunc = handlerFunc
        # FullArgSpec(args=[], varargs=None, varkw=None, defaults=None, kwonlyargs=[], kwonlydefaults={}, annotations={'name': <class 'str'>})
        argsSpec = inspect.getfullargspec(self.handlerFunc)
        self.signature = inspect.signature(self.handlerFunc)
        self.args = argsSpec[0]
        self.kwargs = argsSpec[4]
        self.path = inspect.getsourcefile(self.handlerFunc)
        self.relPath = self.path.replace(basePath,"").rstrip(".py").rstrip("index").strip("/")
        # Register module for later use
        self.module = inspect.getmodule(self.handlerFunc)
        
        if self.module != None and not self.path in modules :
            modules[self.path] = self.module
        elif self.module == None :
            self.module = modules.get(self.path)     

        addToTree(self.path.replace(basePath, ""), self, moduleTree)
    
    def __call__(self, *args,**kwargs) :
        logger.debug('call', *args,**kwargs)
        for key in kwargs :
            if key not in self.kwargs :
                kwargs.pop(key)
        
        ba = self.signature.bind_partial(*args[0:len(self.args)], **kwargs)
        logger.debug('bound', ba)
        return self.handlerFunc(*ba.args, **ba.kwargs)

    def on(self) -> bool :
        return True

    def block(self) -> bool :
        return False

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '{0}:{1}{2}{3}->{4}'.format(id(self), self.handlerFunc.__name__, tuple(self.args), tuple(self.kwargs) , self.path)

def handler(on = None, block = None):
    global Handler
    if not on and not block :
        return Handler
    
    class ExtendedHandler(Handler) :
        def __init__(self, handlerFunc):
            super().__init__(handlerFunc)
            nonlocal on
            self.on = on or True
            nonlocal block
            self.block = block or False

        def on(self) -> bool :
            return self.on() if callable(self.on) else self.on

        def block(self) -> bool :
            return self.block() if callable(self.block) else self.block

    return ExtendedHandler
