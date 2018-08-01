# MTProxy v1.0
Lightweight and easy to set up docker image for MTProto proxy server.

[![Docker Build Status](https://img.shields.io/docker/build/viers/mtproxy.svg)](https://hub.docker.com/r/viers/mtproxy/)
[![](https://images.microbadger.com/badges/image/viers/mtproxy.svg)](https://microbadger.com/images/viers/mtproxy "Image size")


Binary inside: [f9158e3129efd4c from 19 Jul 2018](https://github.com/TelegramMessenger/MTProxy/commit/f9158e3129efd4ccdc291aefb840209791226a77)

### How to run:
All you need is an installed docker. Server can be configured with the special json dictionary file, where all the fields are top level key-value pairs. If the field is absent, it's value is set to default.

* `keys`: An array of client keys, if you have generated some before. By default, this array is empty. 
* `new_keys`: Number of new client keys to generate. If you have no existing keys, you should generate at least one. Default value: 1
* `update_hours`: How often telegram servers list will be updated. Default value: 12.
* `ip`: Server external IP. Necessary for servers behind NAT, also used in invite links, if server URL was not provided. By default is empty.
* `url`: Server URL, if any, to be used in invite links. Default value: same as `ip`.
* `port`: Exposed server port for invite links. Default value: 443.
* `tag`: Your proxy tag, optionally received from [@MTProxyBot](https://t.me/MTProxybot). By default is empty.

Configuration file example:
```json
{
    "keys": [
        "deadbeefdeadbeefdeadbeefdeadbeef"
    ],
    "new_keys": 1,
    "update_hours": 12,
    "ip": "127.0.0.1",
    "url": "my-tgproxy.com",
    "port": 443,
    "tag": "1234554321"
}
```

To be applied, you should mount this file into docker container as `/configuration.json`. Recommended command to launch container:

`docker run -d --restart always -p [port]:443 -v [configuration path]:/configuration.json --name mtproxy viers/mtproxy`

, where `[port]` is the server port, and `[configuration path]` is a full path to your configuration file.

Generated keys and all invite links will be printed in container log. To see the logs, use: `docker logs --follow mtproxy`.

To collect the server stats: `docker exec mtproto curl http://localhost:80/stats`
