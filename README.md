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

## Getting API keys

You will need to get the different API keys and add them to the *credentials.json* file. If you don't want to add one of the features don't worry, just don't add your API keys to the credentials and the specific widget on the User Interface will not be shown.

### RescueTime

RescueTime is a software that measures and tracks what you're doing on your computer and mobile devices. It is launched in the background and do not need any user input. You don't need to have a paid subscription to use this software, the free version (Classic) works!

First go on [Rescue Time](https://www.rescuetime.com/) official website and download the app. Follow the instructions and do not add working hours (TODO: or set up to all day everyday).
You can also download the **RescueTime Classic** app on your mobile device (via the Playstore/AppleStore).

When you use the app, make sure RescueTime is running (otherwise you will have empty graphs on the left panel of the User Interface).

You will also need to get your API key via the ... (https://www.rescuetime.com/anapi/manage)

### WakaTime

WakaTime is the RescueTime/Fitbit for developers. It gets you metrics, insights, and time tracking automatically generated from your programming activity. You need to create an account on [WakaTime](https://wakatime.com/) and install the extension on your preferred IDE (e.g. for [Visual Studio Code](https://wakatime.com/vs-code)). You don't need to have the premium plan to integrate WakaTime to the Productivity dashboard.

Then create an API key via [Secret API Key](https://wakatime.com/settings/api-key).

### Spotify

You already know Spotify. We will use it here to listen to music based on your mood. For the spotify integration you need to have a premium account. (TODO: explore LastFM for non Spotify subscriber, not sure really need Spotify premium). First, create a [Spotify for developers](https://developer.spotify.com/) account, and from the dashboard *create an app*. You will get a public and private key, and add them to the *credentials.json*.

### TODOIST

Todoist is a task-manager and to-do list app to become more focused, organized and not forget important tasks. The way I use it is that everyday, at the end of my work session, I make a 10-minute day review and set up the work for the day after. This way I create tasks with order of importance (from 1 to 4) and set the date to finish all this. Then, those tasks that are due either the current day or the day after, or that are overdue, shown in sorted order of priority. You can also download the app on your mobile device to update tasks from there!

First, create an account and login at [Todoist](https://todoist.com). Then, at the top-right, click your avatar. select *Settings*, to the left, select *Integrations*, select the *Developer* tab and click Copy to clipboard to get your API token. The paste it to the *credentials.json*.

You first need to create a project called **Work** (we will only show tasks that are in the work project so that personal/home tasks are not showned during work time). Then add a section called *Work TODO* (upper-right three dots then *Add section*) and add your tasks with priority and due date to the section.

Do not forget to do this everyday and update tasks based on your daily advances!

### Timer

I am a fan of the Pomodoro technique for deep work when I am working and that is why I implemented a Timer frame (down-right of the User Interface) that I use to fullfill my overall daily goals. Indeed, RescueTime keeps tracking your time while you're absent of your screen but your screen is still running. Thus, the timer can be paused if interruptions to your workflow happen. You can also enter offline work (e.g. meeting) that counts towards your daily time objectives. You can setup your daily goal in the config file (TODO: add config). WARNING: do not set-up too big objectives: indeed, even if you are super productive, do not set-up your goal too high. If you spend 8h30 at your desk you won't be productive for 8h30. The Pomodoro technique is intentionaly focus on deep work and thus you need to take break between sessions. For example, if I spend 9 hours working, I will only make 9 Pomodoro sessions of 50minutes each (which is 7h30 of focus work). In-between each Pomodoro session I take a 10-minute break. I also spend some time between sessions to check my emails (10min total, instead of the 10min break after the last pomodoro before lunch, inside a Pomodoro session if need to make a long answer) and do the daily review at the end of the day (10min, instead of the break of the last pomodoro session). This adds up to a total time of (50*9+10*9) of 9 hours of work. And do not forget your longer lunch break!

Would you like to see a pop-up that ask you why did you pause your work to better analyze your focus sections?

To save your data, the ideal would be to have a Database online but as most of the services are not free, we will only automatically save the Timer data to your personal Google Drive server. For this, you need to connect to your Google account and go to [Google Cloud API and services](https://console.cloud.google.com/apis) and create a project. Then add a *Service account* and allow spreadsheet API. The copy the e-mail of the Service and go to your Google Drive account and create empty spreadsheets called: *offline_work.csv* and *timer_data.csv*. Then right-click on the sheet one at a time and select share and add the email you^ve copied before to the shared user. This will allow you to automatically write to the files from Python's code.
