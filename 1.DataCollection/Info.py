import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

users = pd.read_csv('users_one_year.csv')
lists = pd.read_csv('lists1.csv')
relations = pd.read_csv('realtion1.csv')
silver_lists = pd.read_csv('golden_lists.csv')

error_users = users.loc[users['got_tweets'] == -1]
print("#users with problem ---> ", len(error_users))

print("users tweets description: ")
print(users['last_year_tweets'].describe())

print("users likes description: ")
print(users['last_year_likes'].describe())

users[['last_year_likes', 'last_year_tweets']].plot(kind='box')
plt.semilogy()

no_tweets = users.loc[users['last_year_tweets'] == 0]
print("#users with no tweets ---> ", len(no_tweets))

no_likes = users.loc[users['last_year_likes'] == 0]
print("#users with no likes ---> ", len(no_likes))

inactive_users = users.loc[(users['last_year_likes'] == 0) & (users['last_year_tweets'] == 0)]
print("#inactive_users ---> ", len(inactive_users))

active_users = users.loc[users['last_year_likes'] + users['last_year_tweets'] > 300]
print("#inactive_users ---> ", len(active_users))

print("users tweets description: ")
print(active_users['last_year_tweets'].describe())

print("users likes description: ")
print(active_users['last_year_likes'].describe())

active_users[['last_year_likes', 'last_year_tweets']].plot(kind='box')

# plt.semilogy()
# plt.show()

print("-------------------------------- lists info ----------------------------------------")

active_users_relations = relations.loc[relations['user_id'].isin(active_users['id'].to_list())]
print("active_users_relations length ---> ", len(active_users_relations))

active_users_lists = active_users_relations.drop_duplicates(subset='list_id', keep="last")
print("active_users_lists length ---> ", len(active_users_lists))

count_users_in_lists = active_users_relations[['user_id', 'list_id']].groupby('list_id').count().reset_index() \
    .sort_values(['user_id'], ascending=False)

lists_with_two_users = count_users_in_lists.loc[count_users_in_lists['user_id'] > 1]
print('lists_with_two_users length ---> ', len(lists_with_two_users))

lists_with_three_users = count_users_in_lists.loc[count_users_in_lists['user_id'] > 2]
print('lists_with_three_users length ---> ', len(lists_with_three_users))

gold_lists = lists.loc[lists['id'].isin(lists_with_two_users['list_id'].to_list())]
print('gold_lists length ---> ', len(gold_lists))

lists_with_two_users[['user_id']].plot(kind='box')
lists_with_three_users[['user_id']].plot(kind='box')
# plt.show()

print("list users description: ")
print(lists_with_two_users[['user_id']].describe())

print("\n list tweets description: ")
print(silver_lists[['got_tweets']].describe())

error_lists = silver_lists.loc[silver_lists['got_tweets'] == -1]
print("#error_lists ---> ", len(error_lists))

empty_lists = silver_lists.loc[silver_lists['got_tweets'] == 0]
print("#empty_lists ---> ", len(empty_lists))

active_lists = silver_lists.loc[silver_lists['got_tweets'] > 300]
print("#active_lists ---> ", len(active_lists))

active_lists[['got_tweets']].plot(kind='box')
print("\n active list tweets description: ")
print(active_lists[['got_tweets']].describe())
# plt.show()

gl = relations[relations['list_id'].isin(active_lists['id'].to_list())]
gu = gl[gl['user_id'].isin(active_users['id'].to_list())]
valid_users_id = gu['user_id'].unique()
golden_lists_id = gu['list_id'].unique()
print("#valid_users ---> ", len(valid_users_id))

golden_lists = active_lists.loc[active_lists['id'].isin(golden_lists_id)]
print("#golden_lists ---> ", len(golden_lists))
# golden_lists.to_csv('golden_lists-final.csv', index=False)


valid_users = active_users.loc[active_users['id'].isin(valid_users_id)]
print("#valid_users ---> ", len(valid_users))

m = np.zeros([len(valid_users) + 1, len(golden_lists) + 1])
for index, row in gu[['user_id', 'list_id']].iterrows():
    user_index = np.where(valid_users == row[0])[0][0]
    list_index = np.where(golden_lists == row[1])[0][0]
    m[user_index][list_index] = 1
np.set_printoptions(threshold=np.inf)
y = m.sum(axis=0)  # how many user for each list
x = m.sum(axis=1)  # how many list for each user

count = len([i for i in x if i > 1])
print('#relation with 2 lists', count)

count = len([i for i in x if i > 2])
print('#relation with 3 lists', count)

count = len([i for i in x if i > 3])
print('#relation with 4 lists', count)

count = len([i for i in x if i > 4])
print('#relation with 5 lists', count)

users_indexes = [i for i in range(len(x)) if x[i] > 2]
print(users_indexes)
golden_users = valid_users.iloc[users_indexes]
# golden_users.to_csv('golden_users-final.csv', index=False)
