# HCDE 310 Final Project - SpotiTube
This final project was created by Michael Wentworth using Spotify API and YouTube API

The project is a Flask web application using Python, HTML, CSS, and Javascript to create a locally hosted website that connects to a user's Spotify account and displays the music video for the currently playing song on Spotify.

The only API key that may need to be modified is the youtubeKey, which is defined in app.py on line 10. This key is from YouTube's API website and is limited to a quota of 10,000 per day. One refresh of the /watchvideo route on the application costs 100 quota, which is the cost of one search call on YouTube's API. This means that the site can only refresh 100 times per day, so if the quota limit is reached, youtubeKey can be changed to a new API key to override this quota limit.