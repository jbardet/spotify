# Spotify
SQL and Data Visualization project on Spotify Data

## How to get your data

You can ask to access your [personal spotify data](https://support.spotify.com/us/article/data-rights-and-privacy-settings/). This request can take up to 30 days and eventually you will get an email with your Spotify data in a *.zip* file. Extract the MyData folder and copy it in your working folder.

The JSON files we are interested in are grouped by year and named as such: *Streaming_History_Audio_2015-2017_0.json*.

To access to song features, we need to register to [Spotify Developer](https://developer.spotify.com/). Then, go to your developer dashboard and click on ‘Create an App’. Then you can use Python's library *Spotipy* to create API requests to get features of songs, podcasts and artists.

## Connect to PostgreSQL

To connect to your database you first need to launch it via:
Create new server: createdb spotifydb (need to add to path or launch from C:\Program Files\PostgreSQL\15\bin)

If need: suppress db: dropdb mydb

Activate DB: psql spotifydb

Open psql for trobleshooting: psql -U postgres, quit: \q
List databases: \l

-> now have features and spotify_artists