# MTProxy v1.2
Lightweight and easy to set up docker image for the MTProto proxy server.

[![Docker Build Status](https://img.shields.io/docker/build/viers/mtproxy.svg)](https://hub.docker.com/r/viers/mtproxy/)
[![Docker Pulls](https://img.shields.io/docker/pulls/viers/mtproxy.svg)](https://hub.docker.com/r/viers/mtproxy/)
[![MicroBadger Size](https://images.microbadger.com/badges/image/viers/mtproxy.svg)](https://microbadger.com/images/viers/mtproxy)

Binary inside: [dc0c7f3de from 9 Oct 2019](https://github.com/TelegramMessenger/MTProxy/commit/dc0c7f3de40530053189c572936ae4fd1567269b)

### How to run:
All you need is an installed docker. A server must be configured with the special json dictionary file, mounted as `/configuration.json`.

Configuration file will be modified by the server itself, so that the generated data will be kept after a restart. Changing this file on the host would not affect the server until the manual container restart.

Configuration parameters:

* `keys`: An array of client keys, that have been generated before. Empty by default.
* `new_keys`: Number of new client keys to generate. Server should have at least one key to be accessible. Default value: 1
* `update_hours`: How often telegram servers list will be updated (in hours). Default value: 12.
* `ip`: Server external IP. Necessary for servers behind NAT, also used in invite links, if server URL was not provided. Empty by default.
* `url`: Server URL, if any, to be used in invite links. Default value: same as `ip`.
* `port_stats`: Port for HTTP Stats. Default value: 80
* `port`: Exposed server port for invite links. Default value: 4000.
* `fake_tls_domain`: Fake-TLS domain. **Important!** Specifying this value disables all the other transports.
* `tag`: Your proxy tag, optionally received from [@MTProxyBot](https://t.me/MTProxybot). Empty by default.

To launch container: `docker run -d --restart always -p [port]:[port] -v [full-configuration-file-path]:/configuration.json --name mtproxy viers/mtproxy`.

To see the logs: `docker logs --follow mtproxy`.

To collect server stats: `docker exec mtproxy curl http://localhost:[port_stats]/stats`

Example Configuration:
```
{
  "keys": [],
  "new_keys": 1,
  "fake_tls_domain": "microsoft.com",
  "ip": "",
  "url": "",
  "port": 4000,
  "update_hours": 12,
  "port_stats": 80,
  "tag": ""
}
```
