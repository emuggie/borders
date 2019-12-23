import logging
from pprint import pformat

class Logger :
    def __init__(self, name):
        self.name = name
        self.logger = None
        
    def debug(self, *args, **kwargs):
        self.logger = self.logger if self.logger else logging.getLogger(self.name)
        self.logger.isEnabledFor(logging.DEBUG) and self.logger.debug(toStr(args, kwargs))

    def info(self, *args, **kwargs):
        self.logger = self.logger if self.logger else logging.getLogger(self.name)
        self.logger.isEnabledFor(logging.INFO) and self.logger.info(toStr(args, kwargs))

    def warn(self, *args, **kwargs):
        self.logger = self.logger if self.logger else logging.getLogger(self.name)
        self.logger.isEnabledFor(logging.WARN) and self.logger.warn(toStr(args, kwargs))

    def error(self, *args, **kwargs):
        self.logger = self.logger if self.logger else logging.getLogger(self.name)
        self.logger.isEnabledFor(logging.ERROR) and self.logger.error(toStr(args, kwargs))

def toStr(args, kwargs) :
    txt = ""
    for arg in args :
        txt = txt + (arg  if type(arg) == str else '{0}'.format(pformat(arg))) + ' '
    
    for key, val in kwargs :
        txt = txt + '{0}:{1}'.format(key,val if type(val) == str else pformat(val)) + ' '
    
    return txt

loggers = {}

def getLogger(name:str) -> Logger :
    logger = loggers.get(name)
    if logger == None :
        logger = Logger(name)
        loggers.update({ name : logger })
    return logger


