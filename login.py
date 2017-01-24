from user import User
from database import Database
from twitter_utils import consumer, get_request_token, get_oauth_verifier, get_access_token

# Initializes de database
Database.initialise(user='postgres', password='sancas', database='twitter-exercise', host='localhost')

# Ask the user for an email and checks if its in the database
user_screen_name = raw_input("What is your screen_name ")

# this will return a user object. If email didn't exist it wound't pass an object, because it will be None.
user = User.load_from_db_by_email(user_screen_name)

# This runs if the user doesn't exists (is not None), so we have to register a new user
if not user:

	# get all credentials from Twitter to make requests
	request_token = get_request_token()
	oauth_verifier = get_oauth_verifier(request_token)
	access_token = get_access_token(request_token, oauth_verifier)

	# Creates a user within the Database with all its data
	user = User(user_screen_name, access_token['oauth_token'], access_token['oauth_token_secret'], None)
	user.save_to_db()

tweets = user.twitter_request('https://api.twitter.com/1.1/search/tweets.json?q=computers+filter:images')

for tweet in tweets['statuses']:
	print(tweet['text'])