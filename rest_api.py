#!/usr/bin/env python
import json
import config
import sys
import re
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from flask import Flask, request
from werkzeug.exceptions import NotFound, Unauthorized, BadRequest

app = Flask(__name__)
app.debug = True
app.config['CORS_HEADERS'] = ['Content-Type', 'X-API-KEY']
cors = CORS(app)


def check_auth():
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        raise Unauthorized()
    u = User.check_api_key(api_key)
    if not u:
        raise Unauthorized()
    return u


def construct_owm_req_uri(city, country):
    return config.OWM_API_REQ_URI_TEMPLATE % {'city': city, 'country': country, 'api_key': config.OWM_API_KEY}

print(construct_owm_req_uri('Melbourne', 'au'))

@app.route('/weather', methods=['GET'])
def get_weather():
    # sanitize

    # auth

    # req

    # description
    return 'ok'



if __name__=='__main__':
    http = WSGIServer(('', config.PORT), app)
    http.serve_forever()
