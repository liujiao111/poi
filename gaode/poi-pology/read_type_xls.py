

import pandas as pd


data = pd.read_csv("gaode-poi.csv")

type_codes = []

str_ss= ''
for index,row in data.iterrows():
    str_ss += str(row['min_type']) + ","


ls = []
for sf in str_ss.strip(",").split(","):
    ls.append(sf)


print(len(list(set(ls))))

print(list(set(ls)))


