#
# A simple endpoint that can receive documents from an external source, mark them up and return them.  This can be useful
# for hooking in callback functions during indexing to do smarter things like classification
#
from flask import (
    Blueprint, request, abort, current_app, jsonify
)
import fasttext
import json
from nltk.stem.snowball import SnowballStemmer

STEMMER = SnowballStemmer("english")

THRESHOLD = 0.9

bp = Blueprint('documents', __name__, url_prefix='/documents')

def get_synonyms(model, name):
    name = name.lower()
    punctuation = "!#$%&'()*+,-./:;<=>?@[\]^_`{|}~®™"  # excluding " (inches)
    name = "".join([char for char in name if char not in punctuation])
    name = " ".join(name.split()) # remove extra space
    tokens = name.split()
    stems = [STEMMER.stem(token) for token in tokens]

    synonyms = set()
    for stem in stems:
        nn_model = model.get_nearest_neighbors(stem, k=20)
        nn_match = [nn[1] for nn in nn_model if nn[0] > THRESHOLD]
        synonyms.update(nn_match)
    return " ".join(synonyms)

# Take in a JSON document and return a JSON document
@bp.route('/annotate', methods=['POST'])
def annotate():
    if request.mimetype == 'application/json':
        the_doc = request.get_json()
        response = {}
        cat_model = current_app.config.get("cat_model", None) # see if we have a category model
        syns_model = current_app.config.get("syns_model", None) # see if we have a synonyms/analogies model
        # We have a map of fields to annotate.  Do POS, NER on each of them
        sku = the_doc["sku"]
        for item in the_doc:
            the_text = the_doc[item]
            if the_text is not None and the_text.find("%{") == -1:
                if item == "name":
                    if syns_model is not None:
                        print("IMPLEMENT ME: call nearest_neighbors on your syn model and return it as `name_synonyms`")
                        response['name_synonyms']=get_synonyms(syns_model, the_text)
                        print(response)
        print(response)
        return jsonify(response)
    abort(415)
