import csv
import os
import pandas as pd
from dao import DAO, VOTE_DB_FILE, root_dir
from itertools import combinations

member_id = 'B001230'

def jaccard(X:pd.Series):
    intersection = (X == 0).sum()
    union = len(X) - X.isna().sum()

    if union:
        return intersection/union
    else:
        return 0
def jaccard_correlate(df, outfilename):
    cc = list(combinations(df.columns, 2))
    df_pairs = pd.concat([df[c[1]].sub(df[c[0]]) for c in cc], axis=1, keys=cc)
    vote_jaccard = {rep1: {rep2: 0.0 for rep2 in df.columns} for rep1 in df.columns}
    for column in df_pairs:
        rep1, rep2 = column
        vote_jaccard[rep1][rep2] = jaccard(df_pairs[column])
        vote_jaccard[rep2][rep1] = jaccard(df_pairs[column])
    df_jaccard = pd.DataFrame(vote_jaccard)
    df_jaccard.to_csv(outfilename)
def correlate(df, outfilename):
    corr_df = df.corr()
    print(corr_df)
    corr_df.to_csv(outfilename)

db = DAO(VOTE_DB_FILE)
vote_result = db.get_votes()
df_raw = pd.DataFrame(vote_result.rows,
                      columns=['voted_on', 'congress_number', 'rollcall_number', 'name', 'vote'])
df_raw['vote'] = df_raw['vote'].map({'Yes':1, 'No':0, 'Not Voting':None})

df_vote = df_raw.pivot(index='voted_on', columns='name', values='vote')

print(df_vote)
corr_out_file = os.path.join(root_dir, "data", "senate_correlation.csv")
#correlate(df_vote,corr_out_file )
jaccard_correlate(df_vote, corr_out_file)

