import pandas as pd
import tweepy
import datetime
import pytz
import time
import json
from pandas import json_normalize

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

login = pd.read_csv('login.csv')
consumer_key = login['key'][0]
consumer_secret = login['key'][1]
access_token = login['access'][0]
access_tokenSecret = login['access'][1]

# create auth object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

# set access token and access token secret
auth.set_access_token(access_token, access_tokenSecret)

# create api object
# api = tweepy.API(auth, wait_on_rate_limit=True)
api = tweepy.API(auth, proxy='socks5h://localhost:9150', wait_on_rate_limit=True)

#  Extract lists tweets between a specific time
# datetime object is naive
startDate = datetime.datetime.now() - datetime.timedelta(days=30)

# convert datetime object to aware
utc = pytz.UTC
startDate = utc.localize(startDate)

# create lists dataframe
lists_db = pd.DataFrame(
    columns=['id', 'name', 'subscriber_count', 'member_count', 'mode', 'description', 'last_tweet_date', 'processed'])
try:
    df = pd.read_csv('lists1.csv')
    if not df.empty:
        lists_db = pd.concat([lists_db, df])
except Exception as e:
    pass
lists_db = lists_db[
    ['id', 'name', 'subscriber_count', 'member_count', 'mode', 'description', 'last_tweet_date', 'processed']]

# create relations dataframe
users_lists_db = pd.DataFrame(columns=['user_id', 'list_id'])
try:
    df = pd.read_csv('realtion1.csv')
    if not df.empty:
        users_lists_db = pd.concat([users_lists_db, df])
except Exception as e:
    pass
users_lists_db = users_lists_db[['user_id', 'list_id']]

# create users dataframe
users_db = pd.DataFrame(columns=['id', 'name', 'screen_name', 'followers_count', 'friends_count', 'processed'])
try:
    df = pd.read_csv('users1.csv')
    if not df.empty:
        users_db = pd.concat([users_db, df])
except Exception as e:
    seed = api.get_user(screen_name='aplusk')
    ith_list = [seed.id, seed.name, seed.screen_name, seed.followers_count, seed.friends_count, 0]
    users_db.loc[len(users_db)] = ith_list

users_db = users_db[['id', 'name', 'screen_name', 'followers_count', 'friends_count', 'processed']]


def scrapUsers(user_id):
    try:
        # Collect lists using the Cursor object
        lists = tweepy.Cursor(api.get_list_subscriptions, user_id=user_id).items(10)

        # Store these lists into a python list
        user_lists = [l for l in lists]

        count = 0
        for l in user_lists:
            id = l.id
            name = l.name
            if len(name) > 2:
                subscriber_count = l.subscriber_count
                if subscriber_count > 10:
                    member_count = l.member_count
                    mode = l.mode
                    description = l.description
                    if mode == 'public':
                        last_tweet = api.list_timeline(list_id=id, count=1)
                        if len(last_tweet) > 0:
                            last_tweet_date = last_tweet[0].created_at
                            if last_tweet_date > startDate:
                                ith_list = [id, name, subscriber_count, member_count, mode, description,
                                            last_tweet_date, 0]
                                if not (users_lists_db[['user_id', 'list_id']].values == [user_id, id]).all(
                                        axis=1).any():
                                    users_lists_db.loc[len(users_lists_db)] = [user_id, id]
                                    users_lists_db.to_csv('realtion1.csv', index=False)
                                    # Append to dataframe - lists_db
                                if id not in lists_db.id.values:
                                    print("list added: ", id)
                                    lists_db.loc[len(lists_db)] = ith_list
                                count += 1
        return count
    except tweepy.errors.TweepyException as e:
        print("Error for ", user_id, ": ", e)
        return -1


def scrapLists(list_id):
    try:
        # Collect Users using the Cursor object
        users = tweepy.Cursor(api.get_list_subscribers, list_id=list_id).items(50)

        # Store these lists into a python list
        list_subscribers = [u for u in users]

        count = 0
        for u in list_subscribers:
            id = u.id
            name = u.name
            if len(name) > 2:
                screen_name = u.screen_name
                friends_count = u.friends_count
                followers_count = u.followers_count
                ith_list = [id, name, screen_name, followers_count, friends_count, 0]
                if not (users_lists_db[['user_id', 'list_id']].values == [id, list_id]).all(axis=1).any():
                    users_lists_db.loc[len(users_lists_db)] = [id, list_id]
                    users_lists_db.to_csv('realtion1.csv', index=False)
                # Append to dataframe - users_db
                if id not in users_db.id.values:
                    users_db.loc[len(users_db)] = ith_list
                    print("user added: ", id)
                count += 1
        return count
    except tweepy.errors.TweepyException as e:
        print("Error for ", list_id, ": ", e)
        return -1


if not users_db.empty:
    for index1, users in users_db.loc[users_db['processed'] == 0].iterrows():
        print("lists for ----> ", users.id)
        result = scrapUsers(user_id=users.id)
        if result > 0:
            users_db.loc[users_db['id'] == users.id, 'processed'] = result
        elif result == -1:
            users_db.loc[users_db['id'] == users.id, 'processed'] = -1
        else:
            users_db.loc[users_db['id'] == users.id, 'processed'] = -2

        df = lists_db
        df.to_csv('lists1.csv', index=False)
        df = users_db
        df.to_csv('users1.csv', index=False)

for index, lists in lists_db.loc[lists_db['processed'] == 0].iterrows():
    if pd.isnull(lists.id):
        break
    result1 = scrapLists(list_id=lists.id)
    if result1 == -1:
        lists_db.loc[lists_db['id'] == lists.id, 'processed'] = -1
    elif result1 > 0:
        lists_db.loc[lists_db['id'] == lists.id, 'processed'] = result1
    else:
        lists_db.loc[lists_db['id'] == lists.id, 'processed'] = -2

    df = lists_db
    df.to_csv('lists1.csv', index=False)
    df = users_db
    df.to_csv('users1.csv', index=False)
