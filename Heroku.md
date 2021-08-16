# Heroku

## Container
```
heroku config:set POD_PREFIX=* -a bot-recorder

```

## Scaling
```
heroku ps:scale web=0 -a audio-tube
```
## Debug
```
heroku run bash -a audio-tube
```
## Plugins
```
heroku plugins:install heroku-builds
heroku builds -a audio-tube
heroku builds:cancel -a YOUR_HEROKU_APP_NAME
```
