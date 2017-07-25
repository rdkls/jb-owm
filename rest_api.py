#!/usr/bin/env python
import config
import util
import re

import sys
import json
import redis
import requests

from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from flask import Flask, request
from werkzeug.exceptions import NotFound, Unauthorized, BadRequest, TooManyRequests, BadGateway

from models import User


app = Flask(__name__)
app.debug = True
app.config['CORS_HEADERS'] = ['Content-Type', 'X-API-KEY']
cors = CORS(app)

# Redis connection instance for this worker
redis_db_ratelimit = redis.Redis(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_DB_RATELIMITS)

def check_auth():
    #api_key = request.headers.get('X-API-KEY')
    api_key = request.args.get('api_key')
    if not api_key:
        raise Unauthorized()
    user = User.get_user_from_api_key(api_key)
    if not user:
        raise Unauthorized()
    return user

def check_ratelimit(api_key):
    return true

@app.route('/weather', methods=['GET'])
def get_weather():
    # Auth
    user = check_auth()

    # check throttling
    # raise TooManyRequests

    # Extract and sanitize city & country
    q = request.args.get('q')
    if not q:
        raise BadRequest('q parameter required')

    # We're only supporting ?q=cityname[,countryname]
    # So we'll just remove anything that's not (alphanum or comma),
    # complain if more than one comma
    # and pass the ?q straight through to OWM
    q = re.sub('[^\w,]', '', q)
    if q.count(',') > 1:
        raise BadRequest('q parameter should be of format cityname[,countryname]')

    # Request to OWM
    url = util.construct_owm_req_uri(q)
    res = requests.get(url)

    # Grab the first weather item's description
    # (according to doco looks like we only get more than one if specifying geo region)
    # If the format isn't exactly as expected, or other problem talking to OWM
    # (e.g. bad API key) just log this and return 502 bad gateway
    try:
        j = res.json()
        description = j['weather'][0]['description']
    except:
        # TODO log the invalid req/res from OWM for troubleshooting, raise an alert etc
        # Error returned to client intentionally vague
        raise BadGateway('Problem talking to weather service')

    return description


if __name__=='__main__':
    http = WSGIServer(('', config.LISTEN_PORT), app)
    http.serve_forever()
