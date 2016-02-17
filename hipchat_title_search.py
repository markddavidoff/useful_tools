"""
A simple script to get data from hipchat users. If you use the description/title field on
hipchat, this can provide usefull utilites (at bottom) such as searching users by title.

- Mark Davidoff, 2016, Reserved
"""

# url of your hipchat server
HIPCHAT_SERVER_URL = "<sub>.hipchat.com"

# token used to access hipchat api. Easiest is a personal access token:
# https://www.hipchat.com/account/api
# https://developer.atlassian.com/hipchat/guide/hipchat-rest-api/api-access-tokens
ACCESS_TOKEN =  '<token>'

# when retrieving user info, how often to print number remaining
print_every_x_count = 5 #defualt prints remaining after every 5 users processed

import requests
from collections import defaultdict
try:
    # if already loaded, don't load again
  role_dict
  print "using cached user list.."
except NameError:
    get_users_url = 'https://{}/v2/user?auth_token={}'.format(HIPCHAT_SERVER_URL, ACCESS_TOKEN)
    get_user_info_url = 'https://{}/v2/user/{}?auth_token={}'.format(HIPCHAT_SERVER_URL,'{}', ACCESS_TOKEN)
    print "retrieving list of users..."
    r = requests.get(get_users_url)
    users = r.json['items']
    user_ids = [user['id'] for user in users]


role_dict = defaultdict(list)
total = len(user_ids)
print "retrieving details for {} users...".format(total)
count = 0

for u_id in user_ids:
    count += 1
    if count % print_every_x_count == 0:
        print "{} remaining...".format(total-count)
        
    url = get_user_info_url.format(u_id)
    r = requests.get(url)
    resp = r.json
    # print "retrieved name: {} role: {}...".format(resp['name'],resp['title'])
    role_dict[resp['title']].append(resp['name'])

def print_all():
    """
    Print list of all users grouped by title
    """
    for role, person_list in role_dict.iteritems():
        print "{}:{}".format(role,person_list)
    
def has_role(r):
    """
    Find users by role
    r: a string in a role a user has
    e.g.
    has_role('account') will return all account managers
    and accountants grouped by common titles
    """
    for role, person_list in role_dict.iteritems():
        if r in role.lower():
            print "{}:{}".format(role,person_list)

def what_do(name):
    """
    Find user(s) title
    name: a string in a person's name
    e.g.
    what_do('john') returns all johns and their titles
    """
    for role, person_list in role_dict.iteritems():
        for person in person_list:
            if name in person.lower():
                print "{}:{}".format(role, person)
                
print "use print_all() to print all roles and users"
print "use has_role(<word in role>) to find a role"
print "use what_do(<word in user name>) to find a user"
