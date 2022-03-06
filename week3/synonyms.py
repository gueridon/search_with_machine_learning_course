import fasttext
from nltk.stem.snowball import SnowballStemmer

STEMMER = SnowballStemmer("english")
input_file = "/workspace/datasets/fasttext/titles.txt"
model = fasttext.train_unsupervised(input_file, "skipgram", epoch=25, minCount=5)

candidates = [
'speaker',
'receiver',
'camera',
'laptop',
'blender',
'philips',
'whirlpool',
'kitchenAid',
'nikon',
'hp',
'easyshare',
'xbox 360',
'razr',
'inspiron',
'officejet',
'mocha',
'stainless steel',
'12"',
'45w',
'500gb']

threshold = 0.75

for candidate in candidates:
    stemmed_candidate = STEMMER.stem(candidate)
    print(f"{candidate}, {stemmed_candidate}")
    synonyms = model.get_nearest_neighbors(stemmed_candidate)
    for synonym in synonyms:
        
        if synonym[0] >= threshold:
            print("\t", synonym[0], synonym[1])