import argparse
import os
import string
import random
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
from nltk.stem.snowball import SnowballStemmer

STEMMER = SnowballStemmer("english")

def transform_name(product_name, stemmer=True):
    # IMPLEMENT
    product_name = product_name.lower()
    punctuation = "!#$%&'()*+,-./:;<=>?@[\]^_`{|}~®™"  # excluding " (inches)
    product_name = "".join([char for char in product_name if char not in punctuation])
    product_name = " ".join(product_name.split()) # remove extra space
    if stemmer:
        tokens = product_name.split()
        stems = [STEMMER.stem(token) for token in tokens]
        product_name = " ".join(stems)
    return product_name

# Directory for product data
directory = r'/workspace/search_with_machine_learning_course/data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
# general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")
general.add_argument("--output", default="/workspace/datasets/product_data/categories/output.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=1.0, type=float, help="The rate at which to sample input (default is 1.0)")

# IMPLEMENT: Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")
general.add_argument("--build", default=False, type=bool, help="Rebuild output")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
    os.mkdir(output_dir)

if args.input:
    directory = args.input
# IMPLEMENT:  Track the number of items in each category and only output if above the min
min_products = args.min_products
sample_rate = args.sample_rate
build = args.build
print(build)
if build:
    print("Writing results to %s" % output_file)
    with open(output_file, 'w') as output:
        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                print("Processing %s" % filename)
                f = os.path.join(directory, filename)
                tree = ET.parse(f)
                root = tree.getroot()
                for child in root:
                    if random.random() > sample_rate:
                        continue
                    # Check to make sure category name is valid
                    if (child.find('name') is not None and child.find('name').text is not None and
                        child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
                        child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None):
                        # Choose last element in categoryPath as the leaf categoryId
                        cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
                        # if len(child.find('categoryPath')) >= 2:
                        #     # replace with parent level -2, -3 
                        #     cat = child.find('categoryPath')[len(child.find('categoryPath')) - 2][0].text
                        # Replace newline chars with spaces so fastText doesn't complain
                        name = child.find('name').text.replace('\n', ' ')
                        # print(cat, name, transform_name(name, stemmer=False))
                        output.write("__label__%s %s\n" % (cat, transform_name(name, stemmer=True)))

# filter my min_products
print(f"Value of min_products: {min_products}")
df = pd.read_csv('/workspace/datasets/product_data/categories/output.fasttext', names=['cat_name'])
print(f"Number of products before filtering: {len(df)}")
df[['cat','name']] = df["cat_name"].str.split(" ", 1, expand=True)
cat_count = pd.DataFrame(df["cat"].value_counts().reset_index().values, columns=["cat", "count"])
print(f"Number of categories before filtering: {len(cat_count)}")
select_min_products = cat_count.loc[cat_count['count'] > min_products]
cat_to_keep = select_min_products['cat'].tolist()
df = df[df['cat'].isin(cat_to_keep)]
print(f"Number of products after filtering: {len(df)}")
print(f"Number of categories after filtering: {len(select_min_products)}")
df = df.drop(['cat', 'name'], axis = 1)
df.to_csv("/workspace/datasets/product_data/categories/output_filtered.fasttext", header=False, index=False)