# MTProto
Easy-configurable docker image for MTProto proxy server.

[![](https://images.microbadger.com/badges/image/viers/mtproto.svg)](https://microbadger.com/images/viers/mtproto "Image size")

### How to run:
All you need is installed docker and filled json configuration file (see configuration.json.example). Parameters are:
* existing_keys: Array of client keys, if you have generated them before. 
* keys_to_generate: Number of new client keys to generate.
* update_period_hours: How often server will be updating core configuration. Recommended value - 24.
* server_url: Server URL is necessary for generating invite link.
* server_port: Server port is also necessary for invite link (default value - 443).

Command to launch server itself:

`docker run -d --restart always -v [configuration path]:/configuration.json -p 443:[server port] --name mtproto viers/mtproto`
* [server port]: same value as server_port in configuration file.
* [configuration path]: full path to your configuration file.

To see logs, generated and existing keys and invite links: `docker logs --follow mtproto`.

To collect the server stats: `docker exec mtproto curl http://localhost:80/stats`
