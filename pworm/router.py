import threading, weakref
from typing import Any, List, Dict
from types import SimpleNamespace
import asyncio

from .loader import moduleTree, Handler
from .logging import getLogger
from .data import Stack, Queue
logger = getLogger(__name__)

MAX_CHAIN = 50

eventLoop = asyncio.get_event_loop()
_contextMap = weakref.WeakKeyDictionary()

class RequestContext :
    def __init__(self):
        global MAX_CHAIN
        self._pathStack = []
        self._waitQueue = Queue(MAX_CHAIN)
        self._callStack = Stack(MAX_CHAIN) # type: List[Handler]
        self.local = LazySimpleNamespace()
        self._local = SimpleNamespace()

    def addQueue(self, *handlers:Handler)-> bool :
        """
        Add handler to waitQueue.
        Retrun True if blocks after
        """
        for handler in handlers :
            if handler == None :
                continue
            # to offer handler scoped values
            self._callStack.put(handler)
            if handler.on() :
                self._waitQueue.put(handler)
            block = handler.block() 
            # remove after invocation overs
            self._callStack.get()
            if block :
                break
        return block
    
    def proceed(self, *args, **kwargs) -> Any :
        if not self.hasNext() :
            logger.debug('Next chain not found, arguments:', *args, **kwargs)
            return None
        
        handler = self._waitQueue.get()
        currentWaits = self._waitQueue.size()
        # handler scoped : callstack will always increase.
        self._callStack.put(handler)
        logger.debug('Proceed call chain:', handler)
        returned = handler(*args, **kwargs)
        logger.debug('Returned : ', returned)
        # Force proceed if user hasn't wrapped proceed.
        if self._waitQueue.size() > 0 and currentWaits == self._waitQueue.size() :
            logger.debug('Proceed not invoked. force proceeding')
            returned = self.proceed(returned) or returned
        return returned

    def hasNext(self) :
        return self._waitQueue.size() > 0

    def isValid(self) :
        # TODO : Should add case for passing only cases : Exact Match but don't serve?
        print("111111",self._waitQueue._list,self.getRequestPath(),self._waitQueue.last().relPath)
        if self._waitQueue.size() == 0  :
            return False
        if self.getRequestPath().rstrip("/index").strip("/") == self._waitQueue.last().relPath :
            return True
        if not self._waitQueue.last().block() :
            return False
        return True

    def getCurrentHandler(self) :
        return self._callStack.peek()

    def getCurrentPath(self) -> str :
        return self.getCurrentHandler().relPath

    def getRequestPath(self) -> str :
        return self._pathStack[-1]
    
    def isExactPath(self) -> bool :
        return self.getRequestPath().rstrip("/index").strip("/") == self.getCurrentPath()

class LazySimpleNamespace(SimpleNamespace) :
    def __getattribute__(self, name):
        return getContext()._local.__getattribute__(name)
    
    def __setattr__(self, name, value) :
        getContext()._local.__setattr__(name, value)

def getContext() -> RequestContext:
    try :
        logger.debug('getTask :get_running_loop()') 
        ctx = asyncio.Task.current_task()
        if ctx == None :
            raise
    except : 
            logger.debug('getTask : from Thread') 
            ctx =  threading.current_thread()
    
    global _contextMap
    if not ctx in _contextMap :
        _contextMap.update({ctx : RequestContext() })
    return weakref.proxy(_contextMap.get(ctx))

def getRequestPath() -> str :
    return getContext()._pathStack[-1]
    
def getCurrentPath() -> str :
    return getContext().callStack[getContext().callStackIdx].relPath

def isExactPath() -> bool :
    return getContext().isExactPath()

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
    context._pathStack.append(path)
    logger.debug("Routing : ", getRequestPath(), context)
    path = path.strip("/")
    startFrom = startFrom.strip("/")
    relPath = path.lstrip(startFrom)

    currentNode = moduleTree
    for subPath in startFrom.split("/") :
        if subPath == "" or subPath == None :
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
        if indexs != None and context.addQueue(*indexs) :
            break

        # End of path
        if subPath == None :
            break

        endPoints = currentNode.get(subPath + ".py")
        if endPoints != None and context.addQueue(*endPoints) :
            break

        subTree = currentNode.get(subPath)
        # Suspended on middle
        if subTree == None :
            break

        currentNode = subTree

    logger.debug('callstack', context._callStack)
    # Panic if path doesn't match
    if not context.isValid() :
        raise(PathNotFoundError("Page Not Found"))

    result = context.proceed(args, kwargs)
    # Remove path stack
    
    logger.debug('Result from path:',context._pathStack.pop()," -> ", result)
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