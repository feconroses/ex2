from database import CursorFromConnectionFromPool
import oauth2
import json
from twitter_utils import consumer

# from database import connect

class User:
    def __init__(self, screen_name, oauth_token, oauth_token_secret, id):
        self.screen_name = screen_name
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.id = id

    def __repr__(self):
        return "<User {}>".format(self.screen_name)

    def save_to_db(self):
        # creates a connection, creates a cursor, after it inserts data by commiting it and finally it closes the connection
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('INSERT INTO users (screen_name, oauth_token, oauth_token_secret) VALUES (%s, %s, %s)',
                           (self.screen_name, self.oauth_token, self.oauth_token_secret))

    @classmethod
    def load_from_db_by_screen_name(cls, screen_name):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('SELECT * FROM users WHERE users.screen_name=%s', (screen_name,))
            user_data = cursor.fetchone()  # returns the first value as its assume the screen name is unique
            if user_data:
                return cls(user_data[1], user_data[2], user_data[3], user_data[0]) # creating an object and returning screen name, oauth, oauth secret and ID

    def twitter_request(self, uri, verb='GET'):
        # Create an 'authorized_token' Token object and use that to perform Twitter API calls on behalf of the user
        authorized_token = oauth2.Token(self.oauth_token, self.oauth_token_secret)
        authorized_client = oauth2.Client(consumer, authorized_token)

        response, content = authorized_client.request(uri, verb)
        if response.status != 200:
            print ("An error occurred when searching!")

        return json.loads(content.decode('utf-8'))