from api import *
from dao import DAO, VOTE_DB_FILE

"""
Pro Publica API
https://projects.propublica.org/api-docs/congress-api/
"""

Current_Congress = '117'

def get_all_votes(year, month):
    '''
    First get all roll call numbers for the given year & month
    Then get all the votes for each roll call number
    Record in database
    If the voting member does not exist in our member table, add them first
    :param year:
    :param month:
    :return:
    '''
    results = api_get_rollcall(year, month)
    if not results:
        return

    db = DAO(VOTE_DB_FILE)
    for vote in results:
        rollcall_number = vote['roll_call']
        question = vote['question']
        description = vote['description']
        vote_date = vote['date']
        vote_time = vote['time']
        #  "2017-01-31" + "12:33:00", -> 'YYYY-MM-DD HH:MM:SS.mmmmmm'
        vote_timestamp = "{} {}.000000".format(vote_date, vote_time)
        congress_number = vote['congress']
        congress_session = vote['session']
        chamber = vote['chamber']

        rollcall_result = db.add_rollcall(question, description, vote_timestamp, congress_number, chamber, congress_session, rollcall_number)
        rollcall_id = rollcall_result.rowid
        results = api_get_rollcall_vote(congress_number, chamber, congress_session, rollcall_number)
        if not results:
            return

        record = {}
        for result in results:
            member_id = result['member_id']
            update_member(db, member_id)

            vote = result['vote_position']
            record[member_id] = (vote)
            rv = db.add_vote(member_id, rollcall_id, vote)
            print('      ', vote_timestamp, vote,)
        print('--\n')

def update_member(db, member_id):
    member_db = db.get_member(member_id)
    if not member_db.status:
        # Need to add new result to DB result table
        result = api_get_member(member_id)
        if not result:
            return
        name = format_name(result["first_name"], result["middle_name"], result["last_name"], result["suffix"])
        db_result = db.add_member(member_id, name)
        print(name)

        for role in result['roles']:
            congress_number = role['congress']
            cmember = db.get_congress_member(congress_number, member_id)
            if not cmember.status:
                # Need to add this role to congress result table
                state = role['state']
                chamber = role['chamber']
                party = role['party']
                print('      ', chamber, congress_number, state, party,)
                db.add_congress_member(congress_number, member_id, state, chamber, party)
        print('')

def format_name(first_name, middle_name, last_name, suffix):
    name = ''
    if first_name:
        name += first_name
    if middle_name:
        name += ' ' + middle_name
    if last_name:
        name += ' ' + last_name
    if suffix:
        name += ' ' + suffix
    return name

"""
UPDATE rollcall
SET voted_on = "2021-07-20 18:01:01.000000"
WHERE id=566
"""

get_all_votes(2021, 2)

done = {
    2022:[ 10, 9, 8, 7, 6, 5, 4, 3, 2, 1 ],
    2021:[ 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2 ]
}
