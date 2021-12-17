import json, requests
from flask import Flask, request, url_for, session, redirect, render_template
import jinja2
import time

app = Flask(__name__)

client_id = "a92d9285d08c4251a961f131f4d5a7e3"
client_secret = "9754b1c4fd054ac2b746482f79bd9616"
youtubeKey = "AIzaSyAcf-MRptiKfEZOGVdwN_BkhQUM90vp63I"
baseurl = "https://api.spotify.com/v1/"

# CURRENT ACCESS TOKEN
app.token = {}
app.currentsong = ""
app.query = ""

@app.route('/')
def home():
    return render_template('home.html', token = app.token)


@app.route('/authorize')
def authorize():
    try:
        response = requests.get(
            "https://accounts.spotify.com/authorize",
            {
                "client_id": client_id,
                "response_type": "code",
                "redirect_uri": url_for('authRedirect', _external=True),
                "scope": "user-read-currently-playing",
                "show_dialog": "true"
            }
        )
        response.raise_for_status()
        return redirect(response.url)
    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)

@app.route('/redirect')
def authRedirect():
    authCode = request.args.get('code')
    authState = request.args.get('state')
    authError = request.args.get('error')
    try:
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            {
            "grant_type": "authorization_code",
            "code": authCode,
            "redirect_uri": url_for('authRedirect', _external=True),
            "client_id": client_id,
            "client_secret": client_secret
            }
        )
        response.raise_for_status()
        app.token = response.json()
        return redirect(url_for('home', _external=False))
    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)

@app.route('/watchvideo', methods = ['GET', 'POST'])
def watchvideo():
    start = time.time()
    url = baseurl + "me/player/currently-playing"
    try:
        response = requests.get(
            url,
            headers={
                "Authorization": app.token['token_type'] + " " + app.token['access_token']
            }
        )
        response.raise_for_status()
        response = response.json()
    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)

    if not response['is_playing']:
        return "Please have a song playing on Spotify and refresh!"


    query = response['item']['name'] + " - "
    query += response['item']['artists'][0]['name']
    for j in response['item']['artists'][1:]:
        query += ", " + j['name']

    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            {
                "key": youtubeKey,
                "part": "snippet",
                "order": "relevance",
                "q": query,
                "maxResults": 1,
                "type": "video"
            }
        )
        r.raise_for_status()
        r = r.json()

        videoId = r['items'][0]['id']['videoId']
        runtime = time.time() - start
        progress = int((response['progress_ms'] / 1000) + runtime + 1)
        return render_template('watchvideo.html', videoId = videoId, progress = progress,
                               name = response['item']['name'], token = app.token, query = query)
    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)


@app.route('/test')
def test():
    return pretty(app.token)

@app.route('/logout')
def logout():
    app.token = {}
    return redirect(url_for('home'))


def safe_get(url="", headers={}, params={}):
    try:
        response = requests.get(url, headers, params)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)

def safe_post(url="", headers={}, params={}):
    try:
        response = requests.post(url, headers, params)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)



