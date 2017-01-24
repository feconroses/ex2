from flask import Flask, render_template, session, redirect, request, url_for, g
from twitter_utils import get_request_token, get_oauth_verifier, get_oauth_verifier_url, get_access_token
import constants
from user import User
from database import Database
import requests

app = Flask(__name__)

# We have to sign the session with a secret key 
app.secret_key = '1234'


# Initializes de database
Database.initialise(user='postgres', password='sancas', database='twitter-exercise', host='localhost')


# Before the request we check if the user is already loggued in (we have his username) within the session
@app.before_request
def load_user():
	if 'screen_name' in session:
		g.user = User.load_from_db_by_screen_name(session['screen_name']) #g es una variable especial que permanece por fuera del metodo


@app.route('/')
def homepage():
	return render_template('home.html')


@app.route('/login/twitter')
def twitter_login():

	# check if user is already loggued in and redirects him to profile
	if 'screen_name' in session:
		return redirect(url_for('profile'))

	#if it doesn't, we get a request token
	request_token = get_request_token()

	#saves the request token within the user session, so when it leavs to twitter and come back, we remember this request token
	session['request_token'] = request_token

	return redirect(get_oauth_verifier_url(request_token))
	#redirecting the user to Twitter so they can confirm authorization


@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('homepage'))


# This is the page the user returns when authenthicated with Twitter
@app.route('/auth/twitter')
def twitter_auth():
	oauth_verifier = request.args.get('oauth_verifier')
	access_token = get_access_token(session['request_token'], oauth_verifier) #this retrieves the request token from the session and creates an accss token 

	user = User.load_from_db_by_screen_name(access_token['screen_name'])

	# If the user doesn't exist, we save it within the database
	if not user:
		user = User(access_token['screen_name'], access_token['oauth_token'], access_token['oauth_token_secret'], None)
		user.save_to_db()

	session['screen_name'] = user.screen_name
	return redirect(url_for('profile'))


@app.route('/profile')
def profile():
	return render_template('profile.html', user=g.user)


@app.route('/search')
def search():
	query = request.args.get('q')
	tweets = g.user.twitter_request('https://api.twitter.com/1.1/search/tweets.json?q={}'.format(query)) #computers+filter:images

	tweet_texts = [{'tweet': tweet['text'], 'label': 'neutral'} for tweet in tweets['statuses']]

	for tweet in tweet_texts:
		r = requests.post('http://text-processing.com/api/sentiment/', data={'text':tweet['tweet']} )
		json_response = r.json()
		label = json_response['label']
		tweet['label'] = label

	return render_template('search.html', content=tweet_texts)

#set the port of the app
app.run(port=4995, debug=True) # use debug=True for debugging errors on the webapp
