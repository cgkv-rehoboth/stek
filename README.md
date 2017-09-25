[![Stories in Ready](https://badge.waffle.io/cgkv-rehoboth/stek.png?label=ready&title=Ready)](https://waffle.io/cgkv-rehoboth/stek)
## CGKV Woerden Site

<img src="https://raw.githubusercontent.com/cgkv-rehoboth/stek/master/src/assets/resources/images/logo-zwart.png" width="200" />

### Contributing

Just follow the [GitHub Flow](https://guides.github.com/introduction/flow/index.html)

### Getting started

See `docs/getting-started/` for a concise guide on development.

Add a timetable called 'Diensten'

### Production

Make sure...

- ... the server's user has read/write access to the media directory
- ... you have build the staticfiles using in production mode `gulp build:prod`
- ...that the file `src/cgkv/localsettings.py` exists that sets `DEBUG = False` and a secret
db user/password
- ...that you have run `./manage.py collectstatic`

Everytime the staticfiles change, you have to run `collectstatic` and restart the wsgi process.
