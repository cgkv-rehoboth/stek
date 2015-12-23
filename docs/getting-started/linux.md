# Unix, getting started

1. Use your package manager to install `python`, `node`
2. Clone this repository
3. Open a terminal at the root of the repository
4. Run the following commands to create the python and node sandboxes and install the local
   dependencies.

    make install
	  source .virtualenv/bin/activate
	  pip install -r requirements

5. Install gulp globally using npm: `sudo npm install -g gulp`

6. Run the build for the client side files `gulp`

7.  You can now migrate the database (make sure the virtualenv is activated as before) and
    run the development server; from the `src/` run:

    python manage.py migrate
	  python manage.py runserver

8.  You should now be able to visit `localhost:8000` (and `localhost:8000/admin/`) in your browser.

## Post installation

You should create a Django user to be able to login at the admin panel (the following commands are
all manage.py commands):

    createsuperuser

Now you can login and browse around.

## IDE

The windows getting-started guide explains how to set up PyCharm
