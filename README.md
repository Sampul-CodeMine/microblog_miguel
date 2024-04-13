# microblog_miguel
This is a repository to hold the project I replicated from Miguel's tutorial on Flask Mega Improved

## Creating Migration Repository (Flask)

First of all, make sure you have the following packages installed for you to be able to use `Database Migration` with Flask

```shell
(venv) $ pip install flask-sqlalchemy
...
(venv) $ pip install flask-migrate
...
(venv) $
```

Next, run the following command from your virtual environment

```shell
(venv) $ flask db init
Creating directory '/home/tester/microblog/migrations' ...  done
Creating directory '/home/tester/microblog/migrations/versions' ...  done
Generating /home/tester/microblog/migrations/README ...  done
Generating /home/tester/microblog/migrations/script.py.mako ...  done
Generating /home/tester/microblog/migrations/env.py ...  done
Generating /home/tester/microblog/migrations/alembic.ini ...  done
Please edit configuration/connection/logging settings in
'/home/tester/microblog/migrations/alembic.ini' before proceeding.
(venv) $
```

This will create a migrations directory with few files and subdirectory. They are part of your project

## Your First Database Migration

With the migration's repository or directory in okace, we can now make our first migration which will include the first table we have in our project (users).

Run the following code"

```shell
(venv) $ flask db migrate -m "Create Users Table"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user'
INFO  [alembic.autogenerate.compare] Detected added index ''ix_user_email'' on '('email',)'
INFO  [alembic.autogenerate.compare] Detected added index ''ix_user_username'' on '('username',)'
  Generating
  /home/tester/microblog/migrations/versions/16ba27a02d54_create_users_table.py ...  done
(venv) $
```

This output or script generated does nothing much but prepares your project for migrating to a newer definition for your database structure or rolling back to a previously defined structure using the `upgradde()` and `downgrade()` functions respectively provided in the generated script.

To finally apply the changes after migration, just run `flask db upgrade`

```shell
(venv) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 16ba27a02d54, Create Users Table
(venv) $
```

## Creating User Login and Password Hashing

When creating a user login system, it is necessary you always remember never to store plain-texted passwords as provided by the users in your database.

That is why we will be using the functionalities from the package `Werkzeug`.

```shell
(venv) $ flask shell
Python 3.8.10 (default, Nov 22 2023, 10:22:35) 
[GCC 9.4.0] on linux
App: app
Instance: /home/tester/microblog/instance
>>> from werkzeug.security import generate_password_hash
>>> hash = generate_password_hash('tester')
>>> hash
'pbkdf2:sha256:600000$RAoKQOzQ7okWzu4I$508494e124f3004db2527e59b654a75d64998109836611501f463eca77353df2'
>>> from werkzeug.security import check_password_hash
>>> check_password_hash(hash, 'testar')
False
>>> check_password_hash(hash, 'tester')
True
>>> 
```

