# jb-owm

## Setup

For 'production', redis server recommended
Recommend running inside docker, takes 5 mins to get running
1. Get docker https://www.docker.com/community-edition
2. docker run -d -p 6379:6379 --name npd_jb_ows_redis redis
3. Test
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
and value = list of request epochs

Each request:
1. Push request epoch on to head of list
2. If length of list < 5 then ALLOW
3. Trim list to 5
4. If tail (oldest) request is within last hour, this means that there have been (at least) 5 requests in the last hour, DENY
5. Otherwise there haven't been 5 requests this hour, ALLOW

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
['2:50', '2:55', '3:05', '3:06', '3:06']

Push, set becomes:
['2:50', '2:55', '3:05', '3:06', '3:06', '3:07']

Trim, set becomes:
['2:55', '3:05', '3:06', '3:06', '3:07']

Tail (earliest) 2:55 is within last hour - DENY

Advantages
- sliding instead of fixed time window; hour boundaries don't cause issues
- simple end efficient data structure and algorithm

Disadvantages
- less performant & more complex than fixed window (e.g. key = apikey + epoch-hour, increment with TTL)


## Testing

## API key
Using demo key from OWM b1b15e88fa797225412429c1c50c122a1


