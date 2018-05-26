# Unix, getting started

- Use your package manager to install `python`, `node`
- Clone this repository
- Open a terminal at the root of the repository
- Run the following commands to create the python and node sandboxes and install the local
   dependencies.

    ```
    make install
    source .virtualenv/bin/activate
    pip install -r requirements

- Run the following commands to install the node sandbox with the dependencies as described by the
   `package.json`:

    ```
    npm install
 
- Install gulp globally using npm: `sudo npm install -g gulp`

- Run the build for the client side files `gulp`

- Download and install MySQL and run the following queries:

    ```
    create database cgkv;
    grant all privileges on cgkv.* to cgkv@localhost identified by 'lCCnO6D9Py1VQukTlGknTnFiNyx6TmJ6';

- Create the tables and insert the default data (make sure the virtualenv is activated as before):

    ```
    python src/manage.py migrate
    python src/manage.py loaddata

-  Run the development server:

    ```
    python src/manage.py runserver

-  You should now be able to visit `localhost:8000` (and `localhost:8000/admin/`) in your browser.

## Post installation

You should create a Django user to be able to login at the admin panel (the following commands are
all manage.py commands):

    createsuperuser

Now you can login and browse around.

## IDE

The windows getting-started guide explains how to set up PyCharm
