import http.server, time, threading, asyncio, cgi, os,urllib.parse,posixpath,json
from urllib.parse import urlparse
from  concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

from sys import platform
from .logging import getLogger
from .router import handle, getContext, PathNotFoundError

logger = getLogger(__name__)

executor = ThreadPoolExecutor()
mp.set_start_method('fork')

resourcePath = os.getcwd()

class DefaultResponseHandler :
    status = 200
    headers = {}
    content = None
    
class ResourcedHandler(http.server.SimpleHTTPRequestHandler) :
    def __init__(self, request, client_address, server):
        self.response = DefaultResponseHandler()
        super().__init__(request, client_address, server)
        
    def list_directory(self, path):
        self.send_error(http.server.HTTPStatus.NOT_FOUND,"Not fd")

    def __getattribute__(self, attr) :
        if attr.startswith("do_") : 
            # Use default HTTP static server if resource exists.
            path = self.translate_path(self.path)
            if os.path.isfile(path) or os.path.isfile(path.rstrip("/")+"/index.htm") or os.path.isfile(path.rstrip("/")+"/index.html"):
                return object.__getattribute__(self, attr)
            # Handle otherwise
            return object.__getattribute__(self, 'do_Handle')
        return object.__getattribute__(self, attr)

    def translate_path(self, path):
        return super().translate_path(path).replace(os.getcwd(), resourcePath, 1)

    def do_Handle(self) :
        parsed_path = urlparse(self.path)
        getContext().local.request = self
        
        try :
            self.parseBody()
            returned = handle(parsed_path.path)
            self.response.content = self.response.content if self.response.content != None else returned
        except  PathNotFoundError :
            # On path not found
            self.send_error(http.server.HTTPStatus.NOT_FOUND,"Not f")
        except Exception as error :
            # On server error
            # logger.error(error)
            self.send_error(http.server.HTTPStatus.INTERNAL_SERVER_ERROR,"Err f")
            raise(error)
        return None
    
    def finish(self) :
        if not self.wfile.closed:
            self.send_response(self.response.status)
            for key in self.response.headers :
                self.send_header(key, self.response.headers[key])
            self.end_headers()
            self.wfile.write(self.response.content if type(self.response.content) == bytes else str(self.response.content).encode('utf-8'))
        super().finish()

    def parseBody(self) :
        if self.command != 'POST' and self.command != 'UPDATE' :
            return
        
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            self.form = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            self.form = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        elif ctype == 'application/json':
            self.json = json.loads(self.rfile.read(length))


class ExtendedHttpServer(http.server.HTTPServer) :
    async def process_request_async(self, request, client_address) :
        logger.debug("Begin Handle Request : ", client_address, request)
        try:
            super().process_request(request, client_address)
        except:
            super().handle_error(request, client_address)
            super().shutdown_request(request)
        logger.debug("End Handle Request : ", client_address, request)

    # Override process_request to delegate execution to threads
    def process_request(self, request, client_address):
        loop = getattr(asyncio,'get_running_loop', asyncio.get_event_loop)()
        loop.run_until_complete(self.process_request_async(request, client_address))
        # loop.run_in_executor(executor, self.process_request_async, request, client_address)
        # executor.submit(self.process_request_thread, request, client_address)

def run(host = "127.0.0.1", port = 5000, handler = ResourcedHandler, interval = 0.5) :
    httpd = ExtendedHttpServer((host, port), handler)
    logger.info("Server :",host, ":", port, "interval : ", interval, ', pid ', os.getpid())

    if platform.startswith("linux") :
        mp.Process(target=httpd.serve_forever,args=(interval,)).start()
    # mp.Process(target=httpd.serve_forever,args=interval).start()
    # mp.Process(target=httpd.serve_forever,args=interval).start()
    httpd.serve_forever(interval)

def test(host = "127.0.0.1", port = 5000, handler = ResourcedHandler, interval = 0.5) :
    """
    Test function for development stage.
    """
    logger.info("Test hosting")
    http.server.HTTPServer((host,port), handler).serve_forever(interval)