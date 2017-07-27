#!/usr/bin/env python
import config
import util

import json
import re
import redis
import fakeredis
import requests
import sys
import time

from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from flask import Flask, request
from werkzeug.exceptions import NotFound, Unauthorized, BadRequest, TooManyRequests, BadGateway

from models import User


app = Flask(__name__)
if config.DEV_MODE:
    app.debug = True
app.config['CORS_HEADERS'] = ['Content-Type', 'X-API-KEY']
cors = CORS(app)

# Redis connection instance for this worker
# Global to the API worker
# Later might do something like a separate service to obtain this, or dependency injection,
# but for now this is good enough
if config.DEV_MODE:
    redis_db_ratelimit = fakeredis.FakeStrictRedis()
else:
    redis_db_ratelimit = redis.Redis(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_DB_RATELIMITS)


def check_api_key():
    api_key = request.args.get('api_key')
    if not api_key:
        raise Unauthorized()
    user = User.get_user_from_api_key(api_key)
    if not user:
        raise Unauthorized()
    return user

def check_ratelimit(api_key):
    """ Implements sliding window rate limit on api requests using redis
    For details see README
    """
    current_request_epoch = time.time()
    # Push current request time on to head of this api key's list
    redis_db_ratelimit.lpush(api_key, current_request_epoch)

    # If this means we're under LIMIT_REQ_PER_HOUR reqs total = ALLOW
    if redis_db_ratelimit.llen(api_key) <= config.LIMIT_REQ_PER_HOUR:
        return True

    # Otherwise - need to check if the oldest req is older than an hour = ALLOW
    current_request_epoch = time.time()
    oldest_request_epoch = float(redis_db_ratelimit.rpop(api_key))
    hours_since_oldest_req = (current_request_epoch - oldest_request_epoch) / 3600
    if hours_since_oldest_req > 1:
        return True

    # Default deny
    return False

@app.route('/weather', methods=['GET'])
def get_weather():
    # Auth
    try:
        user = check_api_key()
    except Unauthorized:
        raise

    # Check throttling
    if not check_ratelimit(user.api_key):
        raise TooManyRequests('Maximum of %s request per hour' % config.LIMIT_REQ_PER_HOUR)

    q = request.args.get('q')
    if not q:
        raise BadRequest('q parameter required')

    # We're only supporting ?q=cityname[,countryname]
    # So we'll just remove anything that's not (alphanum or comma),
    # complain if more than one comma
    # and pass the ?q straight through to OWM (Open Weather Map)
    q = re.sub('[^\w,]', '', q)
    if q.count(',') > 1:
        raise BadRequest('q parameter should be of format cityname[,countryname]')

    # Don't talk to OWM if we're running in dev mode
    if config.DEV_MODE:
        return 'cloudy with a chance of meatballs'

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
        # Error returned to client is intentionally vague
        raise BadGateway('Problem talking to weather service')

    return description


if __name__=='__main__':
    http = WSGIServer(('', config.LISTEN_PORT), app)
    http.serve_forever()
