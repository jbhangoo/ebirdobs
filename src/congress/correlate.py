import os
import pandas as pd
from dao import DAO, VOTE_DB_FILE, root_dir


member_id = 'B001230'

db = DAO(VOTE_DB_FILE)
vote_result = db.get_votes()
votes_df = pd.DataFrame(vote_result.rows,
                        columns=['voted_on', 'congress_number', 'rollcall_number', 'name', 'vote'])
votes_df['vote'] = votes_df['vote'].map({'Yes':1, 'No':0, 'Not Voting':None})
pivot_df = votes_df.pivot(index='voted_on', columns='name', values='vote')
print(pivot_df)

corr_df = pivot_df.corr()
print(corr_df)

corr_out_file = os.path.join(root_dir, "data", "corr_out.csv")
corr_df.to_csv(corr_out_file)
