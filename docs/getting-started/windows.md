# Windooooows, getting started

- Install **Python 3.5** (including pip) from the python site
- Install **NodeJS** (including npm)
- Clone this repository
- Open Powershell at the root of the repository
- Run the following commands to create the python sandbox and install the python dependencies
   as described by the file `requirements`:

    ```
    python -m venv .virtualenv
    .virtualenv\Scripts\activate.ps
    python -m pip install -r requirements

- Run the following commands to install the node sandbox with the dependencies as described by the
   `package.json`:

    ```
    npm install
    npm install -g gulp

- Run the build for the client side files

    ```
    gulp

- Download and install MySQL and run the following queries:

    ```
    create database cgkv;
    grant all privileges on cgkv.* to cgkv@localhost identified by 'lCCnO6D9Py1VQukTlGknTnFiNyx6TmJ6';

- Create the tables and insert the default data (make sure the virtualenv is activated as before):

    ```
    python src/manage.py migrate
    python src/manage.py loaddata

- Download and install PyCharm :

- Configure pycharm. When you open the project it should pick up the virtual python env that we
   created. You should verify this at `Run > Edit Configurations > Python Interpreter`.
   In `Settings > Language and Frameworks > Django` you should set the django root to `src`
   and the settings file to `src/cgkv/settings.py`.

- You can now run django tasks `Tools > Run manage.py Task`. Execute the following in the prompt
    that opens:

    ```
    migrate
    runserver
    
    or continue using the command line:
    
    python src/manage.py runserver

- You should now be able to visit `localhost:8000` (and `localhost:8000/admin/`) in your browser

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
