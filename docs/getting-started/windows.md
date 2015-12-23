# Windooooows, getting started

1. Install **Python 3.5** (including pip) from the python site
2. Install **NodeJS** (including npm)
3. Clone this repository
4. Open Powershell at the root of the repository
5. Run the following commands to create the python sandbox and install the python dependencies
   as described by the file `requirements`:

    python -m venv .virtualenv
	  .virtualenv\Scripts\activate.ps
	  python -m pip install -r requirements

6. Run the following commands to install the node sandbox with the dependencies as described by the
   `package.json`:

	  npm install
	  npm install -g gulp

7. Run the build for the client side files

    gulp

8. Download and install MySQL and run the following queries:

    create database cgkv;
    grant all privileges on cgkv.* to cgkv@localhost identified by 'lCCnO6D9Py1VQukTlGknTnFiNyx6TmJ6';

9. Download and install PyCharm :

11. Configure pycharm. When you open the project it should pick up the virtual python env that we
   created. You should verify this at `Run > Edit Configurations > Python Interpreter`.
   In `Settings > Language and Frameworks > Django` you should set the django root to `src`
   and the settings file to `src/csrdelft/settings.py`.

12. You can now run django tasks `Tools > Run manage.py Task`. Execute the following in the prompt
    that opens:

    migrate
	  runserver

13. You should now be able to visit `localhost:8000` (and `localhost:8000/admin/`) in your browser

## Post installation

You should create a Django user to be able to login at the admin panel (the following commands are
all manage.py commands):

    createsuperuser

Now you can login to the admin and browse around.

## More handy plugins for Intellij

- CSS Support
- Git Integration
- HTML Tools
- NodeJS
- IdeaVim (yeah!)
