# MTProto 1.0
Easy-configurable docker image for MTProto proxy server.

[![](https://images.microbadger.com/badges/image/viers/mtproto.svg)](https://microbadger.com/images/viers/mtproto "Image size")

### How to run:
All you need is installed docker and filled json configuration file.

Configuration file format:
```json
{
    "existing_keys": [
        "deadbeefdeadbeefdeadbeefdeadbeef"
    ],
    "keys_to_generate": 1,
    "update_period_hours": 24,
    "server_url": "127.0.0.1",
    "server_port": 443
}

```
* existing_keys: Array of client keys, if you have generated some before. 
* keys_to_generate: Number of new client keys to generate.
* update_period_hours: How often server will be updating core configuration. Recommended value - 24.
* server_url: Server URL (necessary to generate invite link).
* server_port: Server port (also necessary for invite link), default value - 443.

Command to launch server itself:

`docker run -d --restart always -v [configuration path]:/configuration.json -p 443:[server port] --name mtproto viers/mtproto`
* [server port]: port to expose on server, same as server_port in configuration file.
* [configuration path]: full path to your configuration file.

To see logs, generated and existing keys and invite links: `docker logs --follow mtproto`.

To collect the server stats: `docker exec mtproto curl http://localhost:80/stats`
