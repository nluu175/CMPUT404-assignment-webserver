#  coding: utf-8 
import os
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# Code is written by Nhat Minh, Luu - 2023


def get_request_method(data):
    """
        Returns the method of given request

        Parameters:
            data (str): The request data

        Returns:
            method (str): The method of the request  
    """
    # convert b string to normal string
    method = data[0].decode("utf-8")

    return method

def generate_response_message(code, file_obj=None, content_length=None, content_type=None, location=None):
    """
    Generates and returns the response message according to the given code.

    Parameters:
        code (str): HTTP status code
        file_obj (str, optional, default=None): the content of the file
        content_length (str, optional, default=None): length of content
        content_type (str, optional, default=None): type of content
        location (str, optional, default=None): redirect link (only applicable for code 301)

    Returns:
        response_message (str): the response message 
    """
    status_codes = {
        "200": "OK",
        "301": "Moved Permanently",
        "404": "Not Found",
        "405": "Method Not Allowed"
    }

    if code == "200":
        response_message = f"HTTP/1.1 {code} {status_codes[code]}\r\nContent-type: {content_type}\r\nContent-length: {content_length}\r\n\r\n{file_obj}\r\nConnection: close\r\n"

        return response_message
    
    elif code == "301":
        response_message = f"HTTP/1.1 {code} {status_codes[code]}\r\nContent-type: {content_type}\r\nLocation: {location}\r\nConnection: close\r\n"

        return response_message

    elif code == "404":
        response_message = f"HTTP/1.1 {code} {status_codes[code]}\r\nContent-type: {content_type}\r\nConnection: close\r\n"

        return response_message


    elif code == "405":
        response_message = f"HTTP/1.1 {code} {status_codes[code]}\r\nConnection: close\r\n"
    
        return response_message



class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        # Main logic loop 
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        self.data = self.data.split()

        # method of request is not allowed (only allows HTTP GET)
        if get_request_method(self.data) not in ["GET"]:
            self.request.sendall(bytearray(generate_response_message("405"), "utf-8")) 

        else:
            # we use this to trim down the / at the end of the file (if exists)
            path = os.path.abspath("www") + self.data[1].decode("utf-8")

            if (os.path.exists(path)):
                if path.endswith("html"):
                    content_type = "text/html"
                    file_obj = open(path, "r").read()
                    content_length = str(len(file_obj))

                    self.request.sendall(bytearray(
                        generate_response_message("200", file_obj=file_obj, content_length=content_length, content_type=content_type), 
                        "utf-8")
                    )  
                elif path.endswith("css"):
                    content_type = "text/css"
                    file_obj = open(path, "r").read()
                    content_length = str(len(file_obj))

                    self.request.sendall(bytearray(
                        generate_response_message("200", file_obj=file_obj, content_length=content_length, content_type=content_type), 
                        "utf-8")
                    )  
                
                
                elif path.endswith("/"):
                    path = path + "index.html"
    
                    content_type = "text/html"
                    file_obj = open(path, "r").read()
                    content_length = str(len(file_obj))

                    self.request.sendall(bytearray(
                        generate_response_message("200", file_obj=file_obj, content_length=content_length, content_type=content_type), 
                        "utf-8")
                    )  

                elif ".." in path:
                    # Invalid path, does not allow relative path
                    self.request.sendall(bytearray(generate_response_message("404"), "utf-8")) 

                else:
                    fixed_path = self.data[1].decode("utf-8") + "/"
                    self.request.sendall(bytearray(generate_response_message("301", location=fixed_path), "utf-8"))

            else:
                # Invalid path 
                self.request.sendall(bytearray(generate_response_message("404"), "utf-8")) 


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
