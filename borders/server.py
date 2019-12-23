import http.server, time, threading, asyncio, cgi
from urllib.parse import urlparse
from  concurrent.futures import ThreadPoolExecutor

from .logging import getLogger
from .router import handle, getContext, PathNotFoundError

logger = getLogger(__name__)

PORT = 5000

executor = ThreadPoolExecutor()

class DefaultHandler(http.server.BaseHTTPRequestHandler) :
    def __getattr__(self, attr:str) :
        if attr.startswith("do_") : 
            return self.do_Handle
        return self.__getattribute__(attr)

    def do_Handle(self) :
        parsed_path =urlparse(self.path)
        getContext().local.request = self
        reqInfo = {}
        reqInfo['Client address'] = self.client_address
        reqInfo['Client string'] = self.address_string()
        reqInfo['Command'] = self.method = self.command
        reqInfo['Path'] = self.path
        reqInfo['real path'] = parsed_path.path
        reqInfo['query'] = parsed_path.query
        reqInfo['request version'] = self.request_version
        reqInfo['request version'] = self.request_version
        reqInfo['server_version'] = self.server_version
        reqInfo['sys_version'] = self.sys_version
        reqInfo['protocol_version'] = self.protocol_version
        logger.debug('Request Info :', reqInfo)

        if self.command == 'POST' or self.command == 'UPDATE' :
            pass
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                self.postvars = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                self.postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
            else:
                self.postvars = {}
        
        try :
            handle(parsed_path.path)
        except  PathNotFoundError :
            # On path not found
            self.send_response(404)
            self.end_headers()
            self.wfile.write("Page Not Found !!".encode('utf-8'))
        except Exception as error :
            # On server error
            logger.error(error)
            self.send_response(500)
            self.end_headers()
            self.wfile.write("Internal Server Error".encode('utf-8'))
            raise(error)
        return None

Handler = DefaultHandler

class ExtendedHttpServer(http.server.HTTPServer) :
    # Mimics original behavior including socket close
    def process_request_thread(self, request, client_address):
        try :
            asyncio.set_event_loop(asyncio.new_event_loop())
            asyncio.get_event_loop().run_until_complete(self.process_request_async(request,client_address))
            # asyncio.get_event_loop().run_forever()
        except Exception as er:
            print(er)
    
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
        # loop = asyncio.get_event_loop()
        # loop.run_in_executor(executor, self.process_request_async, request, client_address)
        executor.submit(self.process_request_thread, request, client_address)

def run(host="", port = PORT, handler = Handler, interval=0.5) :
    httpd = ExtendedHttpServer((host, port), handler)
    logger.info("Server Start : , interval : ", host, port, interval)
    httpd.serve_forever(interval)