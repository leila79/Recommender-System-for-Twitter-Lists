import json

import pandas as pd
import tweepy
import datetime
import pytz

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

login = pd.read_csv('login.csv')
consumer_key = login['key'][0]
consumer_secret = login['key'][1]
access_token = login['access'][0]
access_tokenSecret = login['access'][1]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

auth.set_access_token(access_token, access_tokenSecret)

api = tweepy.API(auth, proxy='socks5h://localhost:9150', wait_on_rate_limit=True)

start = datetime.datetime(2020, 1, 1)
end = datetime.datetime(2021, 12, 15)

# convert datetime object to aware
utc = pytz.UTC
start = utc.localize(start)
end = utc.localize(end)


def get_user_info(tweet):
    try:
        user = {'id_str': tweet.user.id_str}
        return user
    except tweepy.errors.TweepyException as e:
        print("problem fetching user info", e)
        return -1


def get_retweet_status(tweet):
    try:
        retweeted_status = None
        if tweet.retweeted_status.lang == 'en':
            retweeted_status = {'created_at': str(tweet.retweeted_status.created_at),
                                'id_str': tweet.retweeted_status.id_str,
                                'full_text': tweet.retweeted_status.full_text,
                                'in_reply_to_status_id_str': tweet.retweeted_status.in_reply_to_status_id_str,
                                'in_reply_to_user_id_str': tweet.retweeted_status.in_reply_to_user_id_str,
                                'retweet_count': tweet.retweeted_status.retweet_count,
                                'favorite_count': tweet.retweeted_status.favorite_count,
                                'lang': tweet.retweeted_status.lang}
            # retweet info
            if hasattr(tweet.retweeted_status, 'retweeted_status'):
                retweeted_status['retweeted_status'] = get_retweet_status(tweet=tweet.retweeted_status)
            # quoted info
            if hasattr(tweet.retweeted_status, 'quoted_status'):
                retweeted_status['quoted_status_id_str'] = tweet.retweeted_status.quoted_status_id_str
                retweeted_status['quoted_status'] = get_quoted_status(tweet=tweet.retweeted_status)
            # retweet entities
            retweeted_status_entities = {'hashtags': tweet.retweeted_status.entities['hashtags'],
                                         'symbols': tweet.retweeted_status.entities['symbols'],
                                         'user_mentions': tweet.retweeted_status.entities['user_mentions'],
                                         'urls': tweet.retweeted_status.entities['urls']}
            retweeted_status['entities'] = retweeted_status_entities
            retweeted_status['user'] = get_user_info(tweet=tweet.retweeted_status)
        return retweeted_status
    except tweepy.errors.TweepyException as e:
        print("problem fetching retweet info", e)
        return -1


def get_quoted_status(tweet):
    try:
        quoted_status = None
        if tweet.quoted_status.lang == 'en':
            quoted_status = {'created_at': str(tweet.quoted_status.created_at),
                             'id_str': tweet.quoted_status.id_str,
                             'full_text': tweet.quoted_status.full_text,
                             'in_reply_to_status_id_str': tweet.quoted_status.in_reply_to_status_id_str,
                             'in_reply_to_user_id_str': tweet.quoted_status.in_reply_to_user_id_str,
                             'retweet_count': tweet.quoted_status.retweet_count,
                             'favorite_count': tweet.quoted_status.favorite_count,
                             'lang': tweet.quoted_status.lang}
            # retweet info
            if hasattr(tweet.quoted_status, 'retweeted_status'):
                quoted_status['retweeted_status'] = get_retweet_status(tweet=tweet.quoted_status)
            # quoted info
            if hasattr(tweet.quoted_status, 'quoted_status'):
                quoted_status['quoted_status_id_str'] = tweet.quoted_status.quoted_status_id_str
                quoted_status['quoted_status'] = get_quoted_status(tweet=tweet.quoted_status)

            # quoted entities
            quoted_status_entities = {'hashtags': tweet.quoted_status.entities['hashtags'],
                                      'symbols': tweet.quoted_status.entities['symbols'],
                                      'user_mentions': tweet.quoted_status.entities['user_mentions'],
                                      'urls': tweet.quoted_status.entities['urls']}
            quoted_status['entities'] = quoted_status_entities
            quoted_status['user'] = get_user_info(tweet=tweet.quoted_status)
        return quoted_status
    except tweepy.errors.TweepyException as e:
        print("problem fetching quote info", e)
        return -1


def get_user_likes(user_id):
    tweets = []
    count = 0
    try:
        for tweet in tweepy.Cursor(api.get_favorites, user_id=user_id, tweet_mode='extended').items():
            lang = tweet.lang
            if count >= 500:
                break
            if tweet.created_at > start and tweet.created_at < end:
                if lang == 'en':
                    created_at = tweet.created_at
                    id = tweet.id
                    full_text = tweet.full_text
                    in_reply_to_status_id_str = tweet.in_reply_to_status_id_str
                    in_reply_to_user_id_str = tweet.in_reply_to_user_id_str
                    in_reply_to_screen_name = tweet.in_reply_to_screen_name
                    retweet_count = tweet.retweet_count
                    is_quote_status = tweet.is_quote_status
                    favorite_count = tweet.favorite_count
                    quoted_status_id_str = None
                    if hasattr(tweet, 'quoted_status_id_str'):
                        quoted_status_id_str = tweet.quoted_status_id_str

                    # tweet entities
                    entities = tweet.entities

                    # user info
                    user = get_user_info(tweet=tweet)

                    retweeted_status = None
                    # retweet info
                    if hasattr(tweet, 'retweeted_status'):
                        retweeted_status = get_retweet_status(tweet=tweet)

                    quoted_status = None
                    # quoted info
                    if hasattr(tweet, 'quoted_status'):
                        quoted_status = get_quoted_status(tweet=tweet)

                    temp_tweet = {'id': id,
                                  'created_at': str(created_at),
                                  'full_text': full_text,
                                  'in_reply_to_status_id_str': in_reply_to_status_id_str,
                                  'in_reply_to_user_id_str': in_reply_to_user_id_str,
                                  'in_reply_to_screen_name': in_reply_to_screen_name,
                                  'is_quote_status': is_quote_status,
                                  'quoted_status_id_str': quoted_status_id_str,
                                  'retweet_count': retweet_count,
                                  'favorite_count': favorite_count,
                                  'lang': lang,
                                  'entities': entities,
                                  'user': user,
                                  'retweeted_status': retweeted_status,
                                  'quoted_status': quoted_status}
                    tweets.append(temp_tweet)
                    count += 1
            if tweet.created_at < start:
                print("get like", tweet.created_at)
                break
        print('get like done',user_id)
        return count, tweets
    except tweepy.errors.TweepyException as e:
        print(e)
        print('error in get_tweet_user:', user_id)
        return -1, tweets


def get_user_tweets(user_id):
    tweets = []
    count = 0
    try:
        # tweet  retweet  reply quote
        for tweet in tweepy.Cursor(api.user_timeline, user_id=user_id, tweet_mode='extended',
                                   include_rts=True, exclude_replies=False).items():
            if count >= 1500:
                break
            if start < tweet.created_at and end > tweet.created_at:
                lang = tweet.lang
                if lang == 'en':
                    created_at = tweet.created_at
                    id = tweet.id
                    full_text = tweet.full_text
                    in_reply_to_status_id_str = tweet.in_reply_to_status_id_str
                    in_reply_to_user_id_str = tweet.in_reply_to_user_id_str
                    in_reply_to_screen_name = tweet.in_reply_to_screen_name
                    is_quote_status = tweet.is_quote_status
                    retweet_count = tweet.retweet_count
                    favorite_count = tweet.favorite_count
                    quoted_status_id_str = None
                    if hasattr(tweet, 'quoted_status_id_str'):
                        quoted_status_id_str = tweet.quoted_status_id_str

                    entities = tweet.entities

                    user = get_user_info(tweet=tweet)

                    retweeted_status = None

                    if hasattr(tweet, 'retweeted_status'):
                        retweeted_status = get_retweet_status(tweet=tweet)

                    quoted_status = None
                    # quoted info
                    if hasattr(tweet, 'quoted_status'):
                        quoted_status = get_quoted_status(tweet=tweet)

                    temp_tweet = {'id': id,
                                  'created_at': str(created_at),
                                  'full_text': full_text,
                                  'in_reply_to_status_id_str': in_reply_to_status_id_str,
                                  'in_reply_to_user_id_str': in_reply_to_user_id_str,
                                  'in_reply_to_screen_name': in_reply_to_screen_name,
                                  'is_quote_status': is_quote_status,
                                  'quoted_status_id_str': quoted_status_id_str,
                                  'retweet_count': retweet_count,
                                  'favorite_count': favorite_count,
                                  'lang': lang,
                                  'entities': entities,
                                  'user': user,
                                  'retweeted_status': retweeted_status,
                                  'quoted_status': quoted_status}
                    tweets.append(temp_tweet)
                    count += 1
            if tweet.created_at < start:
                print("get tweet ", tweet.created_at)
                break
        # like

        print('done ', user_id)
        return count, tweets
    except tweepy.errors.TweepyException as e:
        print(e)
        print('error in get_tweet_user:', user_id)
        return -1, tweets


def run(path):
    users = pd.read_csv(path)
    users = users[['id', 'name', 'screen_name', 'followers_count', 'friends_count', 'processed', 'got_tweets', 'got_likes']]
    tweets_db = pd.DataFrame(columns=['id',
                                      'created_at',
                                      'full_text',
                                      'in_reply_to_status_id_str',
                                      'in_reply_to_user_id_str',
                                      'in_reply_to_screen_name',
                                      'is_quote_status',
                                      'quoted_status_id_str',
                                      'retweet_count',
                                      'favorite_count',
                                      'lang',
                                      'entities',
                                      'user',
                                      'retweeted_status',
                                      'quoted_status'])
    for i in range(len(users)):
        if users.loc[i, 'got_tweets'] == -2 or users.loc[i, 'got_tweets'] == -1:

            tweets_db = tweets_db.iloc[0:0]
            count1, tweets1 = get_user_tweets(user_id=users.loc[i, 'id'])
            count2, tweets2 = get_user_likes(user_id=users.loc[i, 'id'])
            if count1 != -1 and count2 != -1:
                # tweets_db = tweets_db.append(tweets1, ignore_index=True, sort=False)
                # tweets_db = tweets_db.append(tweets2, ignore_index=True, sort=False)
                users.loc[i, 'got_tweets'] = count1
                users.loc[i, 'got_likes'] = count2
                # all_tweets = tweets1 + tweets2
                save_users_tweets(tweets_db=tweets1)
                save_users_tweets(tweets_db=tweets2)

            else:
                users.loc[i, 'got_tweets'] = -1
                users.loc[i, 'got_likes'] = -1

        save_users_status(users=users)


def save_users_status(users):
    users.to_csv('users.csv', index=False)


def save_users_tweets(tweets_db):
    try:
        with open('users_tweets.json', mode='a+', newline='') as file:
            json.dump(tweets_db, file)
            file.write('\n')
        # df = pd.concat([pd.read_json('users_tweets.json', orient='records'), tweets_db])
        # # df.to_csv('users_tweets.csv', index=False)
        # df.to_json('users_tweets.json', orient='records')
    except Exception as e:
        # tweets_db.to_csv('users_tweets.csv', index=False)
        # tweets_db.to_json('users_tweets.json', orient='records')
        print(e)
        print("error in save tweets")


run('users.csv')
