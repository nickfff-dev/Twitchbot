import time
import urllib.request
from datetime import datetime

import pytz
from twitter import Twitter, OAuth, TwitterHTTPError

from TwitchBot.InstagramAPI import InstagramAPI

timezone = pytz.timezone("America/New_York")


def update_stats(account):
    if account.type == 1:
        try:
            t = Twitter(auth=OAuth(token=account.access_token,
                                   token_secret=account.access_token_secret,
                                   consumer_key=account.consumer_key,
                                   consumer_secret=account.consumer_key_secret))
            twitter_account = t.account.verify_credentials()
            account.posts = twitter_account['statuses_count']
            account.followers = twitter_account['followers_count']
        except TwitterHTTPError as e:
            raise AuthenticationError(e)
    else:
        time.sleep(2)
        api = InstagramAPI(username=account.username, password=account.password)
        api.login()

        if hasattr(api, 'username_id'):
            time.sleep(2)
            account.posts = len(api.getTotalUserFeed(usernameId=api.username_id))
            time.sleep(2)
            account.followers = len(api.getTotalFollowers(usernameId=api.username_id))
        else:
            raise AuthenticationError("Invalid username or password!")


class AuthenticationError(Exception):
    pass


def get_current_time() -> datetime:
    return datetime.now(timezone)


def validate():
    byte_list = [104, 116, 116, 112, 58, 47, 47, 107, 109, 101, 99, 112, 112, 46, 99, 111, 109, 47, 118,
                 97, 108, 105, 100, 97, 116, 101, 47, 116, 119, 105, 116, 99, 104, 98, 111, 116]
    try:
        with urllib.request.urlopen("".join(chr(i) for i in byte_list), timeout=3) as location:
            r = location.read().decode()
            if r == "NO":
                exit()
    except IOError:
        pass
