from flask import Flask, render_template, request, Markup, redirect, url_for
import sqlalchemy
import os
from random import choice
from url_handler import validate_url


app = Flask(__name__)
app.secret_key = "<SECRET-KEY>"


# CloudSQL details
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")


# Index page
@app.route('/')
def index():
    return render_template('index.html')


# Shortened URL
@app.route('/short_URL', methods=['GET', 'POST'])
def shorten():

    if request.method == 'POST':

        url_data = request.form['url']
        url_id = url_data[8] + str(choice(range(0, 10))) + "-dt-" + str(choice(range(109, 9999))) + url_data[-2:]
    
        # -------------------------------------------- Valid URL has been provided ------------------------
        if validate_url(url_data) == True:

            # [START cloud_sql_mysql_sqlalchemy_create]
            # The SQLAlchemy engine will help manage interactions, including automatically
            # managing a pool of connections to the database
            db = sqlalchemy.create_engine(
                # Equivalent URL:
                sqlalchemy.engine.url.URL(
                    drivername="mysql+pymysql",
                    username=db_user,
                    password=db_pass,
                    database=db_name,
                    query={"unix_socket": "/cloudsql/{}".format(cloud_sql_connection_name)},
                ),

                # Additional properties here:

                # [START_EXCLUDE]
                # [START cloud_sql_mysql_sqlalchemy_limit]
                # Pool size is the maximum number of permanent connections to keep.
                pool_size=5,
                # Temporarily exceeds the set pool_size if no connections are available.
                max_overflow=2,
                # The total number of concurrent connections for the application will be
                # a total of pool_size and max_overflow.
                # [END cloud_sql_mysql_sqlalchemy_limit]

                # [START cloud_sql_mysql_sqlalchemy_backoff]
                # SQLAlchemy automatically uses delays between failed connection attempts,
                # but provides no arguments for configuration.
                # [END cloud_sql_mysql_sqlalchemy_backoff]

                # [START cloud_sql_mysql_sqlalchemy_timeout]
                # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
                # new connection from the pool. After the specified amount of time, an
                # exception will be thrown.
                pool_timeout=30,  # 30 seconds
                # [END cloud_sql_mysql_sqlalchemy_timeout]

                # [START cloud_sql_mysql_sqlalchemy_lifetime]
                # 'pool_recycle' is the maximum number of seconds a connection can persist.
                # Connections that live longer than the specified amount of time will be
                # reestablished
                pool_recycle=180,  # 3 minutes
                # [END cloud_sql_mysql_sqlalchemy_lifetime]
                # [END_EXCLUDE]
            )
            # [END cloud_sql_mysql_sqlalchemy_create]


            def create_tables():
                """
                Create tables (if they don't already exist)
                """
                with db.connect() as conn:
                    conn.execute(
                        "CREATE TABLE IF NOT EXISTS url_list "
                        "(url_id VARCHAR(20) NOT NULL UNIQUE, url_data VARCHAR(2083) NOT NULL);"
                    )
            #create_tables()


            # [START cloud_sql_mysql_sqlalchemy_connection]
            # Preparing a statement before hand can help protect against injections.
            stmt = sqlalchemy.text(
                "INSERT INTO url_list (url_data, url_id)" " VALUES (:url_data, :url_id)"
            )

            # Check if the URL record exists in the DB already
            try:
                with db.connect() as conn:
                    url_in_db = "SELECT url_id FROM url_list WHERE url_data='" + url_data + "';"
                    url_exists = conn.execute(url_in_db).fetchall()

                    # Check if the URL is in the DB
                    if len(url_exists) > 0:
                        return render_template(
                            'short_URL.html',
                            url=url_data,
                            result="https://forward-url-dot-tsokarev-gcp-test.appspot.com/{}".format(url_exists[0][0])
                        )
            except:
                pass

            try:
                # Using a with statement ensures that the connection is always released
                # back into the pool at the end of statement (even if an error occurs)
                with db.connect() as conn:
                    conn.execute(stmt, url_data=url_data, url_id=url_id)
            except:
                # If something goes wrong, handle the error in this section. This might
                # involve retrying or adjusting parameters depending on the situation.
                # [START_EXCLUDE]
                return render_template('index.html', error="Something went wrong")
            # [END_EXCLUDE]
            # [END cloud_sql_mysql_sqlalchemy_connection]

            return render_template(
                'short_URL.html',
                url=url_data,
                result="https://forward-url-dot-tsokarev-gcp-test.appspot.com/{}".format(url_id)
            )

        # -------------------------------------------- Couldn't validate the URL --------------------------
        else:
            error_msg = validate_url(url_data)
            return render_template('index.html', error=error_msg)


# Routing short URL to the target
@app.route("/<string:id>/")
def forward_to(id):

    # [START cloud_sql_mysql_sqlalchemy_create]
    # The SQLAlchemy engine will help manage interactions, including automatically
    # managing a pool of connections to the database
    db = sqlalchemy.create_engine(
        # Equivalent URL:
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_socket": "/cloudsql/{}".format(cloud_sql_connection_name)},
        ),

        # Additional properties here:

        # [START_EXCLUDE]
        # [START cloud_sql_mysql_sqlalchemy_limit]
        # Pool size is the maximum number of permanent connections to keep.
        pool_size=20,
        # Temporarily exceeds the set pool_size if no connections are available.
        max_overflow=20,
        # The total number of concurrent connections for the application will be
        # a total of pool_size and max_overflow.
        # [END cloud_sql_mysql_sqlalchemy_limit]

        # [START cloud_sql_mysql_sqlalchemy_backoff]
        # SQLAlchemy automatically uses delays between failed connection attempts,
        # but provides no arguments for configuration.
        # [END cloud_sql_mysql_sqlalchemy_backoff]

        # [START cloud_sql_mysql_sqlalchemy_timeout]
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        pool_timeout=30,  # 30 seconds
        # [END cloud_sql_mysql_sqlalchemy_timeout]

        # [START cloud_sql_mysql_sqlalchemy_lifetime]
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # reestablished
        pool_recycle=600,  # 10 minutes, 1800=30 minutes
        # [END cloud_sql_mysql_sqlalchemy_lifetime]
        # [END_EXCLUDE]
    )
    # [END cloud_sql_mysql_sqlalchemy_create]

    original_url = ""
    try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with db.connect() as conn:
            get_url = "SELECT url_data FROM url_list WHERE url_id='" + id + "';"
            original_url = conn.execute(get_url).fetchone()
            if not original_url:
                return render_template('index.html', error="Not Found")
    except:
        # If something goes wrong, handle the error in this section. This might
        # involve retrying or adjusting parameters depending on the situation.
        # [START_EXCLUDE]
        return redirect(url_for('index', error="Not Found"))
    # [END_EXCLUDE]
    # [END cloud_sql_mysql_sqlalchemy_connection]

    return redirect(original_url[0])


if __name__ == "__main__":
    app.run(debug=True)


