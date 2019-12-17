import os
import importlib.util
import threading
import inspect
from typing import Any

BEFORE_FUNC = 'before'
HANDLE_FUNC = 'handle'
AFTER_FUNC = 'after'

# Base import path of modules
basePath = None
modules = {}
moduleTree = {}

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
    return

def lookup() -> None :
    """
    look for python files. 
    """
    global basePath, modules
    basePath = "./" if basePath == None else basePath
    for root, dirs, files in os.walk(basePath) :
        # Ignore hidden directories which starts with '__'
        if root.find("/__") > -1 :
            continue

        # Directory with empty handler
        modules.update({root.replace(basePath,""):[]})

        for file in files :
            if not file.endswith(".py") :
                continue
            filePath = os.path.join(root, file)
            loadModule(filePath)
    # Print total routes
    print(modules, moduleTree)

# Load py file in filePath.
def loadModule(filePath:str, reload:bool = False) -> None : 
    global basePath, modules, moduleTree
    try :
        spec = importlib.util.spec_from_file_location("serverlease.handler", filePath)
        handler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(handler)
        filePath = filePath.replace(basePath, "")
        modules.update({ filePath : handler })
        addToTree(filePath, handler, moduleTree)
    except Exception as error : 
        print(error)

# Add loaded Module to dict tree for route lookup
def addToTree(path:str, handler, treeNode:dict) -> None :
    childPath = path[:path.find("/")] if path.find("/")> -1 else path
    remainPath = path[path.find("/")+1:] if path.find("/")> -1 else None
    if remainPath == None or remainPath == "" :
        treeNode.update({ childPath : handler })
        return
    
    if not childPath in treeNode :
        treeNode.update({ childPath : {} })
        
    addToTree(remainPath, handler, treeNode.get(childPath))
    
    