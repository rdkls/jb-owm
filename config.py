# In production most of this stuff should be set by orchestration, possibly AWS CloudFormation

# Affects:
#   - flask debug mode
#   - using fakeredis instead of real redis DB
#   - contacting OWM API vs. mock response
DEV_MODE            = True

# This is Nick's OWN API key
# Yes it's bad practice, no I don't mind if you use it, no I don't mind distributing this to a potential employer =]
OWM_API_KEY         = '57a72264491277e83b4f7e2ba6b44511'

LISTEN_PORT         = 5000

REDIS_HOST          = '127.0.0.1'
REDIS_PORT          = 6379
REDIS_DB_RATELIMITS = 0

LIMIT_REQ_PER_HOUR  = 5

# In reality these would probably be stored in DB
# mainly for flexibility, facilitate updating them without updating/restarting API code

# Sample
#OWM_API_REQ_URI_TEMPLATE    = 'http://samples.openweathermap.org/data/2.5/weather?q=%(q)s&appid=%(api_key)s'
# Prod
OWM_API_REQ_URI_TEMPLATE =   'http://api.openweathermap.org/data/2.5/weather?q=%(q)s&appid=%(api_key)s'


# Would in a proper app be stored in db, tied to user
VALID_API_KEYS = [
    'd3ea907477b08aa1f3629eccf1817ab7',
    '522748524ad010358705b6852b81be4c',
    '2deb000b57bfac9d72c14d4ed967b572',
    '257c7835ad4c8ffad5059468e0e69aa1',
    'd15338c1e1080b032301667d07460fec'
]

