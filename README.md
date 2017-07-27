# jb-owm

## Setup

### Redis
Redis currently just used for rate limiting, and only if config DEV_MODE is not set

If config.DEV_MODE is set then fakeredis (in-memory) is used, this is intended for development and testing

Recommend to run redis inside docker. For your workstation, brief steps to do so might be:

1. Get docker https://www.docker.com/community-edition

2. Start a new container called e.g. 'npd_jb_ows_redis', using 'redis' image (will download from dockerhub if not available locally), disconnecting after container startup, forwarding port 6379 from the container to local machine:

```docker run -d -p 6379:6379 --name npd_jb_ows_redis redis```

3. Test your redis server is running
```shell
➜  jb-owm git:(master) ✗ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED              STATUS              PORTS                    NAMES
266ec4154194        redis               "docker-entrypoint..."   About a minute ago   Up About a minute   0.0.0.0:6379->6379/tcp   npd_jb_ows_redis
➜  jb-owm git:(master) ✗ nc localhost 6379
set 'd' 'ddd'
+OK
get 'd'
$3
ddd
```

AWS DynamoDB could also be used, but initially would trial / prototype with redis
- simplicity, esp. for development & running locally
- cost
- rate limiting probably not considered 'mission-critical' with AWS' uptime guarantees and scalability required, initially anyway

If redis server is non-localhost and non-default port (6379) these will need to be updated in config.py


### REST API

1. Extract code
2. Edit config.py to set DEV_MODE (and, if not in dev mode, OWM_API_KEY)
3. Strongly recommend using python virtualenv http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/
4. pip install -r requirements.txt
5. ./rest_api.py

## Testing

FakeRedis used to enable unit tests to run locally without setting up redis server; faster for dev and 'close enough' to prod setup

A further step would be integration tests, which would ideally run from CI on full stack, using exactly the same environments as staging / production, with such deployment automated with docker or AWS opsworks


## Rate limiting algorithm

Using redis server vs. within the app process because
- fast, in-memory, small footprint
- supports api worker restart / scaleout / load balancing
- more available for managment & monitoring

Using redis' list data structure
with key = api key
and value = list of request epochs, ordered by time, with the newest request times at head (redis "left") of list

Each request:
1. Push request epoch on to head of list
2. If length of list < 5 then ALLOW
4. If tail (oldest) request is older than an hour = ALLOW (obtain using destructive pop)
5. Otherwise (default) there have been >= 5 requests logged, and the oldest was within the hour = DENY

e.g.

Request @ 2:50
['2:50']
Rule #1 applies - ALLOW

Request @ 2:55
['2:50', '2:55']
Rule #1 applies - ALLOW

Request @ 3:05
['2:50', '2:55', '3:05']
Rule #1 applies - ALLOW

... etc until 5 values ...

Request @ 3:07
Push, set becomes:
['2:55', '3:05', '3:06', '3:06', '3:07']
Tail (oldest) 2:55 is within last hour - DENY

Much later request @ 5:55
Push, set becomes:
['3:05', '3:06', '3:06', '3:07', '5:55']
Tail (oldest) 3:05 is not within last hour - ALLOW


Advantages
- Sliding instead of fixed time window; hour boundaries don't cause issues
- Simple end efficient data structure and algorithm

Disadvantages
- Less performant & more complex than fixed window (e.g. key = apikey + epoch-hour, increment with TTL)
- TBD - locking & possible race conditions

