# import packages and libraries
import numpy as np
import pandas as pd
import plotly.express as px

# reading the dataset
X = list(range(31))
Y =[100*x for x in np.random.randn(31) ]

df = pd.DataFrame(list(zip(X, Y)), columns=['X', 'Y'])
# plot a scatterplot
colorscale = ["red", "yellow", "green"]
fig = px.scatter(df, x='X', y='Y', color='Y',
                 title="Colour palette",
                 color_continuous_scale=colorscale)

fig.show()

"""
# Red to Green through Yellow
colorscale = ["#ff4400;",
"#ff8800;",
"#ffaa00;",
"#ffff00;",
"#aaff00;",
"#88ff00;",
"#44ff00;",
"#00ff00;"
]

"""