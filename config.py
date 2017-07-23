
PORT            = 5000

REDIS_HOST      = '127.0.0.1'
REDIS_PORT      = 6379

# In reality these would probably be stored in DB
# mainly for flexibility, facilitate updating them without updating/restarting API code
OWM_API_REQ_URI_TEMPLATE    = 'http://samples.openweathermap.org/data/2.5/weather?q=%(city)s,%(country)s&appid=%(api_key)s'
OWM_API_KEY     = 'b1b15e88fa797225412429c1c50c122a1'


# Would be stored in db, tied to user
VALID_API_KEYS = [
    'd3ea907477b08aa1f3629eccf1817ab7',
    '522748524ad010358705b6852b81be4c',
    '2deb000b57bfac9d72c14d4ed967b572',
    '257c7835ad4c8ffad5059468e0e69aa1',
    'd15338c1e1080b032301667d07460fec'
]

