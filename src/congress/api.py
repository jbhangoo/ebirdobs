import json
import requests

# The following key has been issued for Congress API
PROPUBLICA_API_KEY = 'J7dshAKeyTGbA3i4FfbJZRmrLTxBlDjbETckjgUY'

# API Base URL and cureent version
PROPUBLICA_API_URL = 'https://api.propublica.org/congress/{version}/'
PROPUBLICA_API_VERSION = 'v1'

MEMBERS_URL = 'https://api.propublica.org/congress/{version}/{congress}/{chamber}/members.json'
MEMBER_URL = 'https://api.propublica.org/congress/v1/members/{member_id}.json'
VOTES_URL = 'https://api.propublica.org/congress/{version}/{congress}/{chamber}/sessions/{session}/votes/{rollcall}.json'
ROLL_CALLS_BY_MONTH_URL = 'https://api.propublica.org/congress/v1/{chamber}/votes/{year}/{month}.json'
ROLL_CALLS_BY_DATES_URL = 'https://api.propublica.org/congress/v1/{chamber}/votes/{start-date}/{end-date}.json'

def HttpGet(api_key, uri: str):
    """
    Low level internal method to perform the API call. Do not call directly
    :param uri:
    :return:    content of successful call or error code
    """
    api_header = {"X-API-KEY": api_key}
    resp = requests.get(uri, headers=api_header)

    if resp.status_code == 200:
        return resp.content
    else:
        return "Error: {}".format(resp.status_code)

def api_get_rollcall(year, month):
    roll_call_url = ROLL_CALLS_BY_MONTH_URL.format(chamber = 'senate', year=year, month=month)
    rollcall_Json = HttpGet(PROPUBLICA_API_KEY, roll_call_url)
    rc_response = json.loads(rollcall_Json)
    if rc_response['status'] == 'OK':
        return rc_response['results']['votes']
    else:
        return {}

def api_get_rollcall_vote(congress, chamber, congress_session, rollcall_number):
    vote_uri = VOTES_URL.format(version=PROPUBLICA_API_VERSION, congress=congress, chamber=chamber,
                                session=congress_session, rollcall=rollcall_number)
    responseJson = HttpGet(PROPUBLICA_API_KEY, vote_uri)
    response = json.loads(responseJson)
    if response['status'] == 'OK':
        return response['results']['votes']['vote']['positions']
    else:
        return {}

def api_get_member(member_id):
    member_uri = MEMBER_URL.format(member_id=member_id)
    memberJson = HttpGet(PROPUBLICA_API_KEY, member_uri)
    mresponse = json.loads(memberJson)
    if mresponse['status'] == 'OK':
        return mresponse['results'][0]
    else:
        return {}

