# MTProto 1.0
Easy-configurable docker image for the MTProto proxy server.

[![](https://images.microbadger.com/badges/image/viers/mtproto.svg)](https://microbadger.com/images/viers/mtproto "Image size")

### How to run:
All you need is an installed docker and filled json configuration file.

Configuration file format:
```json
{
    "existing_keys": [
        "deadbeefdeadbeefdeadbeefdeadbeef"
    ],
    "keys_to_generate": 1,
    "update_period_hours": 24,
    "server_ip": "127.0.0.1",
    "server_port": 443,
    "tag": "1234554321"
}

```
* existing_keys: An array of client keys, if you have generated some before. 
* keys_to_generate: Number of new client keys to generate. Default: 1
* update_period_hours: How often server will be updating core configuration. Default: 24.
* server_url: Server URL (necessary to generate invite link).
* server_port: Server port. Default: 443.
* tag: Your proxy tag.

Command to launch server itself:

`docker run -d --restart always --net "host" -v [configuration path]:/configuration.json --name mtproto viers/mtproto`

, where [configuration path] is a full path to your configuration file.

To see the logs, generated and existing keys and invite links: `docker logs --follow mtproto`.

To collect the server stats: `docker exec mtproto curl http://localhost:80/stats`
