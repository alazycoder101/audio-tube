# Heroku
https://audio-tube.herokuapp.com/

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
#ffmpeg
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git --app audio-tube
heroku plugins:install heroku-builds
heroku builds -a audio-tube
heroku builds:cancel -a YOUR_HEROKU_APP_NAME
```
