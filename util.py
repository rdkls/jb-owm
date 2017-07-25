import re
import config

def construct_owm_req_uri(q):
    return config.OWM_API_REQ_URI_TEMPLATE % {'q': q, 'api_key': config.OWM_API_KEY}

