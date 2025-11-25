# worst-auth

## Description

Minimal auth service

### Dependencies

* import uuid
* import json
* import os
* from http.server import HTTPServer, BaseHTTPRequestHandler
* from urllib.parse import urlparse, parse_qs
* from http.cookies import SimpleCookie

### Installing

* Downloading/Copying the script

### Executing program

just run the command "python ./main.py"

```
python ./main.py
```
To use the API just take the examples from the ./curls.sh.

## Authors

Contributors names and contact info

ex. Gerd Grimmen (F.KU)

## Version History
* 0.4.0
    * rewritten most of the service
    * added /login endpoint
    * added /logout endpoint
    * added functionality for access_token and refresh_token via HttpOnly Cookies -- not yet fully implemented refresh functionality
    * added endpoint functionality to add seperate endpoint programming -- will bring that progress upstream
    * updates to index.html
* 0.3.0
    * added DELETE endpoint for session
* 0.2.0
    * added index.html
    * added endpoint /worst
* 0.1.0
    * Nothing here to see
