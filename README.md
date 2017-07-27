# jb-owm

## Setup

For 'production', redis server recommended

Recommend running inside docker, takes 5 mins to get running
1. Get docker https://www.docker.com/community-edition

2. Start a new container called 'npd_jb_ows_redis', using 'redis' image (will download from dockerhub if not available locally), disconnecting after container startup, forwarding port 6379 from the container to local machine:

```docker run -d -p 6379:6379 --name npd_jb_ows_redis redis```

3. Test it's working
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



## Testing

Redis mock used to enable unit tests to run locally without setting up redis server; faster for dev and 'close enough' to prod setup

A further step would be integration tests, which would ideally run from CI on full stack, using exactly the same environments as staging / production, with such deployment automated with docker or AWS opsworks


## Rate limiting algorithm

Ideally this would use redis because
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
- sliding instead of fixed time window; hour boundaries don't cause issues
- simple end efficient data structure and algorithm

Disadvantages
- less performant & more complex than fixed window (e.g. key = apikey + epoch-hour, increment with TTL)
- TBD - locking & possible race conditions


## Testing

## API key
Using demo key from OWM b1b15e88fa797225412429c1c50c122a1


