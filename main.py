import uuid

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from http.cookies import SimpleCookie

api_data = {
    "access-tokens": {}, "refresh-tokens":{}, "users": {}
}

filename = "api_data.json"

index_content = "Nothing Here!"

PORT = 5020

def write_data():
    with open(filename, "w") as data_file:
        data_file.write(json.dumps(api_data))

def load_index():
    if os.path.isfile("index.html"):
        with open("index.html", "r") as index_file:
            return index_file.read()
    return index_content


def initial_persistence_setup():
    if os.path.isfile(filename):
        with open(filename, "r") as data_file:
            return json.loads(data_file.read())
    else:
        write_data()
        return {"access-tokens": {}, "refresh-tokens":{}, "users": {}}

def create_uuid():
    return str(uuid.uuid4())

class API():
    def __init__(self):
        self.routing = { "GET": { }, "POST": { } , "PUT": { } , "DELETE": { } }

    def get(self, path):
        def wrapper(fn):
            self.routing["GET"][path] = fn
        return wrapper

    def post(self, path):
        def wrapper(fn):
            self.routing["POST"][path] = fn
        return wrapper

    def put(self, path):
        def wrapper(fn):
            self.routing["PUT"][path] = fn
        return wrapper

    def delete(self, path):
        def wrapper(fn):
            self.routing["DELETE"][path] = fn
        return wrapper

api = API()


@api.get("/")
def index(_):
    return {
        "name": "Rest API for simple note taking",
        "summary": "",
        "endpoints": [ "/session", "/worst", "/help" ],
        "version": "0.3.0"
    }

@api.get("/help")
def get_help(args):
    return {"help": "help"}

@api.get("/worst")
def get_worse(args):
    return index_content

@api.post("/")
def post_file(body):
    next_id = str(uuid.uuid4())
    uploaded_file_name = str(next_id) + ".png"
    api_data["session"][str(next_id)] = uploaded_file_name
    write_data()
    return {"id": str(next_id)}


if __name__ == "__main__":
    class ApiRequestHandler(BaseHTTPRequestHandler):
        global api

        def call_api(self, method, path, args):
            if path in api.routing[method]:
                try:
                    result = api.routing[method][path](args)
                    self.send_response(200)
                    self.end_headers()
                    if type(result) is dict:
                        self.wfile.write(json.dumps(result, indent=4).encode())
                    elif type(result) is str:
                        self.wfile.write(result.encode())
                    elif type(result) is bytes:
                        self.wfile.write(result)

                except Exception as e:
                    self.send_response(500, "Server Error")
                    self.end_headers()
                    self.wfile.write(json.dumps({ "error": e.args }, indent=4).encode())
            else:
                self.send_response(404, "Not Found")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "not found"}, indent=4).encode())

        def do_GET(self):
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            args = parse_qs(parsed_url.query)
            if not path in api.routing["GET"]:
                new_path, path_id = path.rsplit("/",1)
                print(new_path, " ", path_id)
                if new_path == "": new_path = "/"
                if new_path in api.routing["GET"]:
                    path = new_path
                    args["path_id"] = path_id
            for k in args.keys():
                if len(args[k]) == 1:
                    args[k] = args[k][0]
            self.call_api("GET", path, args)

        def do_POST(self):
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            if self.headers.get("content-type") != "application/json":
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "posted data must be in json format"
                }, indent=4).encode())
            else:
                data_len = int(self.headers.get("content-length"))
                data = self.rfile.read(data_len).decode()
                self.call_api("POST", path, json.loads(data))

    api_data = initial_persistence_setup()
    index_content = load_index()
    api_data["users"] = {"admin": "admin"}
    httpd = HTTPServer(('', PORT), ApiRequestHandler)
    print(f"Application started at http://127.0.0.1:{PORT}/")
    httpd.serve_forever()