'''
This is the file where all configurables are stored.\n
No other files should be edited unless you're changing the AI model used, or need to change which API you use.
'''

BLACKLIST = {
    "samuellywang@gmail.com": ["wamsang69@gmail.com"],
    "wamsang69@gmail.com": [],
    "samwang@umass.edu": ["wamsang69@gmail.com"]
} # a blacklist, meaning the only senders you do not reply to

WHITELIST = {
    "samuellywang@gmail.com": [],
    "wamsang69@gmail.com": [],
    "samwang@umass.edu": []
} # a whitelist, meaning the only senders you reply to

PREFERRED_MODE = 'blacklist' # CHANGE TO 'whitelist' TO USE WHITELIST

LOGIN_USERS = ["samuellywang@gmail.com", "wamsang69@gmail.com", "samwang@umass.edu"] # users you wish to log in as, if you use multiple accounts
# each account does have to be authenticated separately, but that's because of Google OAuth
# credentials are the same for all accounts though

RELATION = {
    "xin.joy.wang@gmail.com": "My mother",
    "kebinwang@gmail.com": "My father",
    "hliu55@yahoo.com": "My former scoutmaster and mentor to my Eagle Project",
    "wamsang69@gmail.com": "The account I use for auto-mailing"
}
# your relations with other users
# used to help draft more personalized emails
# so please change this for your own situation