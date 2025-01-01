import pandas as pd

cate = pd.read_csv('./data/part.csv')
# print(category.head())
category = []
for i in cate['name']:
    if i not in category:
        category.append(i)
print(category)