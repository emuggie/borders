import threading, weakref
from typing import Any, List, Dict
from types import SimpleNamespace
import asyncio

from .loader import moduleTree, Handler
from .logging import getLogger

logger = getLogger(__name__)

MAX_CHAIN = 20

eventLoop = asyncio.get_event_loop()
_contextMap = weakref.WeakKeyDictionary()

class RequestContext :
    def __init__(self):
        self.pathStack = []
        self.callStack = [] # type: List[Handler]
        self.callStackIdx = -1
        self.local = LazySimpleNamespace()
        self._local = SimpleNamespace()

    def append(self, handler:Handler)-> int :
        # Error if chain exceeds max chain
        self.callStack.append(handler)
        global MAX_CHAIN
        if len(self.callStack) > MAX_CHAIN :
            raise(MaxDepthExceedError("Over 20"))
        return len(self.callStack)

    def validate(self) :
        # TODO : Should add case for passing only cases : Exact Match but don't serve?
        if(len(self.callStack) == 0) :
            return False
        if self.isExactPath() :
            return True
        if not self.callStack[-1].block() :
            return False
        return True

    def getRequestPath(self) -> str :
        return self.pathStack[-1]
    
    def getCurrentPath(self) -> str :
        return self.callStack[self.callStackIdx].relPath

    def isExactPath(self) -> bool :
        return self.getRequestPath().strip("/") == self.getCurrentPath()

    def hasNext(self) -> bool:
        return len(self.callStack) > self.callStackIdx
            
    def proceed(self, *args, **kwargs) -> Any :
        curStackIdx = self.callStackIdx = self.callStackIdx +1
        if not self.hasNext() :
            logger.debug('Next chain not found, return arguments:', *args, **kwargs)
            return tuple(args)
        handler = self.callStack[self.callStackIdx]
        logger.debug('Proceed call chain:', self.callStackIdx, handler)
        returnVal = handler(*args, **kwargs)
        logger.debug('Returned : ', returnVal)
        # Force proceed if user hasn't proceeded.
        if self.callStackIdx == curStackIdx :
            logger.debug('Proceed not invoked. force proceeding to', self.callStackIdx + 1)
            returnVal = self.proceed(returnVal) or returnVal
            logger.debug('Returned : ', returnVal)
        return returnVal

class LazySimpleNamespace(SimpleNamespace) :
    def __getattribute__(self, name):
        return getContext()._local.__getattribute__(name)
    
    def __setattr__(self, name, value) :
        getContext()._local.__setattr__(name, value)

def getContext() -> RequestContext:
    try :
        logger.debug('getTask :get_running_loop()') 
        getLoop = getattr(asyncio,'get_running_loop',asyncio.get_event_loop)
        ctx = asyncio.Task.current_task()
    except Exception as error: 
        try :
            logger.debug('getTask : from main Thread') 
            ctx = asyncio.Task.current_task(eventLoop)
        except Exception as error : 
            logger.debug('getTask : from Thread') 
            ctx =  threading.current_thread()
    
    global _contextMap
    if not ctx in _contextMap :
        _contextMap.update({ctx : RequestContext() })
    return weakref.proxy(_contextMap.get(ctx))

def getRequestPath() -> str :
    return getContext().pathStack[-1]
    
def getCurrentPath() -> str :
    return getContext().callStack[getContext().callStackIdx].relPath

def isExactPath() -> bool :
    return getContext().getRequestPath().strip("/") == getContext().getCurrentPath()

def getLocal()-> Dict :
    return LazySimpleNamespace()

def proceed(*args, **kwargs) :
    return getContext().proceed(*args, **kwargs)

def hasNext() :
    return getContext().hasNext()
    
# Exposed route method
def handle(path:str, startFrom:str = "",*args,**kwargs) -> Any : 
    """
    Invoke handler chain. 
    PathNotFoundError will be thrown if matching handler doesn't exist.\n
    Matching handler satisfies either\n
        - defined in exact path(basePath + requestPath or basePath + requestPath / index ) and 'on'  is function returns true or value True or not defined.\n
        - defined in ancestor path and 'block' is function returns True or value True.\n
    """
    context = getContext()
    context.pathStack.append(path)
    logger.debug("Routing : ", getRequestPath(), context)
    path = path.strip("/")
    startFrom = startFrom.strip("/")
    relPath = path.lstrip(startFrom)

    currentNode = moduleTree
    for subPath in startFrom.split("/") :
        if subPath == "" :
            break
        subTree = currentNode.get(subPath)
        if subTree == None :
            raise(PathNotFoundError('Path Invalid'))
        currentNode = subTree
    
    # Build callstac from path
    subPaths = relPath.split("/")
    subPaths.append(None)
    for subPath in subPaths:
        indexs = currentNode.get("index.py") 
        if indexs != None :
            for index in indexs :
                index.on() and context.append(index)
                if index.block() :
                    break
            if index.block() :
                break

        # End of path
        if subPath == None :
            break

        endPoints = currentNode.get(subPath + ".py")
        if endPoints != None :
            for endPoint in endPoints : 
                endPoint.on() and context.append(endPoint)
                if endPoint.block() :
                    break
            if endPoint.block() :
                break

        subTree = currentNode.get(subPath)
        # Suspended on middle
        if subTree == None :
            break

        currentNode = subTree
    logger.debug('callstack', context.callStack)
    # Panic if path doesn't match
    if not context.validate() :
        raise(PathNotFoundError("Page Not Found"))

    result = context.proceed(args, kwargs)
    # Remove path stack
    
    logger.debug('Result from path:',context.pathStack.pop()," -> ", result)
    return result

class PathNotFoundError(Exception) :
    """
    Thrown when qualified handler is not found.
    """
    def __init__(self, message:str):
        self.message = message

    def __str__(self) :
        return super().__str__()

class MaxDepthExceedError(Exception) :
    """
    Thrown when depth of path exceeds MAX_DEPTH
    """
    def __init__(self, message:str):
        self.message = message

    def __str__(self) :
        return super().__str__()