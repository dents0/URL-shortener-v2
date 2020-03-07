# URL shortener
A **URL shortener** using [Flask](https://flask.palletsprojects.com/en/1.1.x/) on 
[GAE standard](https://cloud.google.com/appengine/docs/standard) and [Cloud SQL](https://cloud.google.com/sql).

How it works
---
1. The form takes a URL checking its format using [url_handler.py](https://github.com/dents0/URL-shortener-v2/blob/master/url_handler.py).
2. If the URL fomat is valid the app checks if the URL is already stored inside the database and, if it is, returns the "shortened" URL.
3. If there is no such URL stored in the db the app adds it there and assigns a "random" unique key to it.
4. The app returns the domain name with the key for that URL as an endpoint *(e.g. **appname-projectname.appspot.com/urlskey** since it's deployed on GAE)*.
5. Once you go to the shortened URL, the app will look up the original URL value in the db searching for it by the unique key provided in the endpoint.

