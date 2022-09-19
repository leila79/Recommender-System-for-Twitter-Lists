# # for tweet in tweepy.Cursor(api.list_timeline, list_id=list_id, tweet_mode='extended', include_rts=True)
import pandas as pd
import tweepy
import datetime
import pytz
import json
from pandas import json_normalize

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

#  Extract lists tweets between a specific time
# datetime object is naive
# startDate = datetime.datetime.now() - datetime.timedelta(days=365)
start = datetime.datetime(2020, 12, 15)
end = datetime.datetime(2021, 12, 15)

# convert datetime object to aware
utc = pytz.UTC
start = utc.localize(start)
end = utc.localize(end)


# # convert datetime object to aware
# utc = pytz.UTC
# startDate = utc.localize(startDate)


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


def get_list_tweets(list_id):
    tweets = []
    count = 0
    try:
        for tweet in tweepy.Cursor(api.list_timeline, list_id=list_id,
                                   tweet_mode='extended', include_rts=True).items():
            # print(tweet.created_at)
            if count > 1000:
                break
            if start < tweet.created_at:
                # print(tweet.id)
                lang = tweet.lang
                if lang == 'en':
                    # print(tweet.lang)
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

                    temp_tweet = {'list_id': str(list_id),
                                  'id': id,
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
                    # print("tweet added: ", id)
                    count += 1
            if tweet.created_at < start:
                print(" < start ")
                break
        print('done', list_id)
        return count, tweets
    except tweepy.errors.TweepyException as e:
        print(e)
        print('error in get_tweet:', list_id)
        return -1, tweets


def run(path):
    lists = pd.read_csv(path)
    lists = lists[['id', 'name', 'subscriber_count', 'member_count', 'mode', 'description',
                   'last_tweet_date', 'processed', 'got_tweets']]
    for i in range(len(lists)):
        if lists.loc[i, 'got_tweets'] == -2 or lists.loc[i, 'got_tweets'] == -1:
            # tweets_db = tweets_db.iloc[0:0]
            count, tweets = get_list_tweets(list_id=lists.loc[i, 'id'])
            #     count:  -1 ==> error   |   -2 ==> found nothing   |  # ==> number of tweet
            if count != -1:
                # tweets_db = tweets_db.append(tweets, ignore_index=True, sort=False)
                lists.loc[i, 'got_tweets'] = count
                save_lists_tweets(tweets)
            else:
                lists.loc[i, 'got_tweets'] = -1

        save_lists_status(lists=lists)


def save_lists_status(lists):
    lists.to_csv('golden_lists_2.csv', index=False)


def save_lists_tweets(tweets_db):
    try:
        with open('lists_tweets.json', mode='a+', newline='') as file:
            # print(tweets_db)
            json.dump(tweets_db, file)
            file.write('\n')

    except Exception as e:
        print(e)
        print("error in save tweets")


run('golden_lists_2.csv')
