# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## Impact of covid on prescribing in March
#
# - [Largest absolute increase in items](#abs)
# - [percentage diff of high volume items](#per)
# - [antibiotics](#abx)
# - [overall trends](#overall)

import pandas as pd
import numpy as np
from ebmdatalab import bq, maps, charts

pd.set_option('display.float_format', lambda x: '%.2f' % x)

# +
sql = '''
WITH
  bnf_tab AS (
  SELECT
    DISTINCT chemical,
    chemical_code
  FROM
    ebmdatalab.hscic.bnf )
SELECT
 SUBSTR(presc.bnf_code, 0, 9) AS chemical_code, 
 chemical,
 SUM(case when month = "2019-03-01" then items else 0 END) as items_2019,
 SUM(case when month = "2020-03-01" then items else 0 END) as items_2020
FROM
ebmdatalab.hscic.normalised_prescribing AS presc
LEFT JOIN
bnf_tab
ON
chemical_code=SUBSTR(presc.bnf_code,0,9)
WHERE
month BETWEEN TIMESTAMP('2019-03-01')
 AND TIMESTAMP('2020-03-01') 
GROUP BY
chemical_code,
chemical
ORDER BY
 items_2020 DESC

  '''

df_chemical = bq.cached_read(sql, csv_path='df_chemical.csv')
df_chemical.head(5)
# -

df_march_diff = df_chemical.copy()
df_march_diff["increase"] = (df_march_diff.items_2020 - df_march_diff.items_2019).fillna(0)
df_march_diff["per_diff"] = 100*((df_march_diff.items_2020 - df_march_diff.items_2019)/df_march_diff.items_2019)
df_march_diff.head(5)


# ## Largest absolute increases in items <a id='abs'></a>

df_march_diff.sort_values("increase", ascending=False).head(26)

# ## Percentage difference <a id='per'></a>

high_volume_diff = df_march_diff.loc[(df_march_diff["items_2020"] >= 50000)].sort_values("per_diff", ascending=False)
high_volume_diff.head(26)

# ## Antimicrobial Stewardship <a id='abx'></a>

df_abx_a = df_march_diff[df_march_diff["chemical_code"].str.startswith("050")].sort_values("increase", ascending=False)
df_abx = df_abx_a.loc[(df_abx_a["items_2020"] >= 5)]
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
df_abx


# ## Overall Trends <a id='overall'></a>

# +
sql2 = '''

SELECT
  month,
  SUM(items) AS items,
  SUM(actual_cost) AS cost
FROM
  ebmdatalab.hscic.normalised_prescribing
WHERE
  month BETWEEN TIMESTAMP('2015-01-01')
 AND TIMESTAMP('2020-03-01') #2014 seems to be duplicated so setting argument to eliminate
GROUP BY
  month
ORDER BY
  items DESC

  '''

df_overall = bq.cached_read(sql2, csv_path='df_overall.csv')
df_overall.head(5)
# -

df_overall.groupby("month").sum().plot(kind='line', title="Trens in items and cost per month since 2015")


