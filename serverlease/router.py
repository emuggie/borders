import os
import importlib.util
import threading
import inspect
from typing import Any
from .loader import moduleTree
from . import types

BEFORE_FUNC = 'before'
HANDLE_FUNC = 'handle'
AFTER_FUNC = 'after'

# Exposed route method
def route(path:str) -> Any :
    path = "/" if path.strip() == "" else path
    path = path if path.endswith("/") else path +"/"
    path = path[1:] if path.startswith("/") else path
    print("Route : ", path)
    return handle(path)

def handle(path:str) -> Any : 
    """
    
    """
    global BEFORE_FUNC, HANDLE_FUNC, AFTER_FUNC
    callStack = []
    returnVal = None
    currentNode = moduleTree

    # Build callstac from path
    for subPath in path.split("/") :
        index = currentNode.get("index.py") 
        endPoint = currentNode.get(subPath + ".py")
        subTree = currentNode.get(subPath)

        print(subPath, index, endPoint, subTree)

        if index != None :
            callStack.append(index)
        if endPoint != None :
            callStack.append(endPoint)
        if subTree == None :
            break

        currentNode = subTree

    # TODO : Chain validation before invoke call stack
    
    # before call
    for handler in callStack :
        if not callable(getattr(handler, BEFORE_FUNC)) :
            continue
        try :
            returnVal = getattr(handler, BEFORE_FUNC)(returnVal) or returnVal
            if type(returnVal) is types.Interrupt :
                break
        except Exception as error:
            print(error)

    # handler call
    if not callable(getattr(handler, HANDLE_FUNC)) :
        return
    try :
        returnVal = getattr(handler, HANDLE_FUNC)(returnVal) or returnVal
    except Exception as error:
        print(error)    
    
    # after call
    for handler in reversed(callStack) :
        if not callable(getattr(handler, AFTER_FUNC)) :
            continue
        try :
            returnVal = getattr(handler, AFTER_FUNC)(returnVal) or returnVal
        except Exception as error:
            print(error)
    
    return returnVal
