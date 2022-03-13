import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv

# Useful if you want to perform stemming.
import nltk
# nltk.download('punkt')
from nltk.tokenize import word_tokenize
STEMMER = nltk.stem.PorterStemmer()

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'

analyzed_queries = r'/workspace/datasets/analyzed_query_data.cvs'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
# general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
# output_file_name = args.output

if args.min_queries:
    min_queries = int(args.min_queries)

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = 'cat00000'

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
for child in root:
    id = child.find('id').text
    cat_path = child.find('path')
    cat_path_ids = [cat.find('id').text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(list(zip(categories, parents)), columns =['category', 'parent'])

# --------------------------------------------------------
# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
CHAR_LIST =  "!#$%&'()*+,-./:;<=>?@[\]^_`{|}~®™"  # excluding " (inches)
def analyze_query(query_str, stemmer=False):
    # IMPLEMENT
    query_str = query_str.lower()
    for char in CHAR_LIST:
        query_str = query_str.replace(char, ' ')
    query_str = " ".join(query_str.split()) # remove extra space
    if stemmer:
        tokens = query_str.split()
        stems = [STEMMER.stem(token) for token in tokens]
        query_str = " ".join(stems)
    return query_str

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
def get_parent_id(category_id):
    if category_id == root_category_id:
        return category_id
    else:
        return parents_df[parents_df.category == category_id]['parent'].values[0]
# --------------------------------------------------------
print("Read the training data into pandas, only keeping queries with non-root categories in our category tree.")
df = pd.read_csv(queries_file_name)[['category', 'query']]
df = df.sample(n=100000) # --------------------------- 50,000 for train and test
print("Apply query analyzer")
df['query'] = df['query'].apply(analyze_query) # ----- apply transform_queries
print("Saving analyzed queries")
df.to_csv(analyzed_queries)

print("Read the analyzed queries")
df = pd.read_csv(analyzed_queries)[['category', 'query']]
print(df.head(5))
df = df[df['category'].isin(categories)]
df = df.dropna() # --------------------------------------- clean up
print(df.head(5))
df['query_count'] = df.groupby('category')['query'].transform(len) # ----- count queries by categories
print(df.head(5))

print("Roll up categories to ancestors to satisfy the minimum number of queries per category.")
# --------------------------------------------------------
df['parent_code'] = df['category'].apply(get_parent_id)# apply get_parents
print(df)
conditions = [
    (df['query_count'] <= min_queries),
    (df['query_count'] > min_queries)
    ]
values = [df['parent_code'], df['category']]

df['category'] = np.select(conditions, values)
print(df.head(5))
# --------------------------------------------------------
print("Number of distinct categories: ", df.category.nunique())


print("Create labels in fastText format.")
df['label'] = '__label__' + df['category']
print(df.head(5))
# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
output_file_name = r'/workspace/datasets/labeled_query_data_' + str(min_queries) + '_b.txt'
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
