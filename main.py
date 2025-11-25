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
    return ({}, {
        "name": "Rest API for auth",
        "summary": "",
        "endpoints": [ "/session", "/worst", "/help" ],
        "version": "0.3.0"
    })

@api.get("/help")
def get_help(args):
    return ({}, {"help": "help"})

@api.get("/worst")
def get_worse(args):
    return ({}, index_content)

@api.get("/worst/<id>")
def get_worse(args, id):
    return ({}, "index_content")

@api.post("/auth/login")
def auth_login(body):
    print(body)
    login_data = body["login"]
    print("name: ", login_data["name"])
    print("password: ", login_data["password"])
    if login_data["name"] in api_data["users"].keys():
        print("login exists")
        if api_data["users"][login_data["name"]] == login_data["password"]:
            print("password is correct")
            return ({"set_access_token": login_data["name"], "set_refresh_token": login_data["name"]}, {"message": "you successfully logged in"})
    write_data()
    # return 401
    return ({},{"id": str(0)})

@api.post("/auth/logout")
def auth_logout(body):
    next_id = str(uuid.uuid4())
    api_data[""][str(next_id)] = uploaded_file_name
    write_data()
    return ({}, {"id": str(next_id)})


if __name__ == "__main__":
    class ApiRequestHandler(BaseHTTPRequestHandler):
        global api
        def run_commands(self, commands):
            if commands == []:
                return
            for command in commands.keys():
                match(command):
                    "set_access_token": 
                        access_token = create_uuid()
                        api_data["access_tokens"] = {access_token: commands[command]}
                        self.send_header("Set-Cookie", f"access_token={create_uuid()}; HttpOnly; SameSite=Strict;") # add Secure for https version
                    "set_refresh_token": 
                        refresh_token = create_uuid()
                        api_data["refresh_tokens"] = {refresh_token: commands[command]}
                        self.send_header("Set-Cookie", f"refresh_token={create_uuid()}; HttpOnly; SameSite=Strict;") # add Secure for https version
                    "void_access_token": 
                        if commands[command] in api_data["access_tokens"].keys(): api_data["access_tokens"].pop(commands[command])
                        self.send_header("Set-Cookie", f"access_token=; HttpOnly; SameSite=Strict; Expires=Thu, 01 Jan 1970 00:00:00 GMT;  Max-Age=0;") # add Secure for https version
                    "void_refresh_token": 
                        if commands[command] in api_data["refresh_tokens"].keys(): api_data["refresh_tokens"].pop(commands[command])
                        self.send_header("Set-Cookie", f"refresh_token=; HttpOnly; SameSite=Strict; Expires=Thu, 01 Jan 1970 00:00:00 GMT;  Max-Age=0;") # add Secure for https version
        
        def call_api(self, method, path, args, in_id=None):
            cookie_headers = self.headers.get("Cookie")
            if cookie_headers:
                print("we've got cookies")
                print(cookie_headers)
                args["access_token"] =cookie_headers["access_token"]
                args["refresh_token"] =cookie_headers["refresh_token"]
            try:
                commands_dict, response = api.routing[method][path](args) if in_id == None else api.routing[method][path](args, in_id)
                self.send_response(200)
                run_commands(commands_dict)
                self.end_headers()

                if type(response) is dict:
                    self.wfile.write(json.dumps(response, indent=4).encode())
                elif type(response) is str:
                    self.wfile.write(response.encode())

            except Exception as e:
                self.send_response(500, "Server Error")
                self.end_headers()
                self.wfile.write(json.dumps({"error": e.args }, indent=4).encode())

        def return_404(self):
            self.send_response(404, "Not Found")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "not found"}, indent=4).encode())
        
        def return_401(self):
            self.send_response(401, "Not Authorized")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "not found"}, indent=4).encode())
        
        def return_400(self):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "posted data must be in json format"}, indent=4).encode())

        def do_GET(self):
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            args = parse_qs(parsed_url.query)
            if path in api.routing["GET"]: 
                self.call_api("GET", path, args)
                return
            else:
                new_path, path_id = path.rsplit("/",1)
                if new_path+"/<id>" in api.routing["GET"]:
                    args["path_id"] = path_id
                    self.call_api("GET", new_path+"/<id>", args, path_id)
                    return
            self.return_404()

        def do_POST(self):
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            if self.headers.get("content-type") != "application/json":
                self.return_400()
            else:
                data_len = int(self.headers.get("content-length"))
                data = self.rfile.read(data_len).decode()
                if path in api.routing["POST"]:
                    self.call_api("POST", path, json.loads(data))
                    return
            self.return_404()
            

    api_data = initial_persistence_setup()
    index_content = load_index()
    api_data["users"] = {"admin": "admin"}
    httpd = HTTPServer(('', PORT), ApiRequestHandler)
    print(f"Application started at http://127.0.0.1:{PORT}/")
    httpd.serve_forever()