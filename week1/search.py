#
# The main search hooks for the Search Flask application.
#
from flask import (
    Blueprint, redirect, render_template, request, url_for
)

from week1.opensearch import get_opensearch

bp = Blueprint('search', __name__, url_prefix='/search')
INDEX_NAME = "bbuy_products"

# Process the filters requested by the user and return a tuple that is appropriate for use in: the query, URLs displaying the filter and the display of the applied filters
# filters -- convert the URL GET structure into an OpenSearch filter query
# display_filters -- return an array of filters that are applied that is appropriate for display
# applied_filters -- return a String that is appropriate for inclusion in a URL as part of a query string.  This is basically the same as the input query string
def process_filters(filters_input):
    filters = []
    display_filters = []  # Also create the text we will use to display the filters that are applied
    applied_filters = ""
    for filter in filters_input:
        print(f"Filter pre-process: {filter}")
        type = request.args.get(filter + ".type")
        filter_to = request.args.get(filter + ".to")
        filter_from = request.args.get(filter + ".from")
        filter_name = request.args.get(filter + ".name")
        filter_key = request.args.get(filter + ".key")
        display_name = request.args.get(filter + ".displayName", filter)
        
        # We need to capture and return what filters are already applied so they can be automatically added to any existing links we display in aggregations.jinja2
        # TODO: IMPLEMENT AND SET filters, display_filters and applied_filters.
        
        # filters get used in create_query below.  display_filters gets used by display_filters.jinja2 and applied_filters gets used by aggregations.jinja2 (and any other links that would execute a search.)
        
        # Filters look like: &filter.name=regularPrice&regularPrice.key={{ agg.key }}&regularPrice.from={{ agg.from }}&regularPrice.to={{ agg.to }}
        
        ## FILTER TYPE == RANGE ########################################################
        if type == "range":
            display_filters.append(f"filter.name={filter}, type={type}, from={filter_from}, to={filter_to}")
            applied_filters += f"&filter.name={filter}&{filter}.type={type}&{filter}.from={filter_from}" \
                                f"&{filter}.to={filter_to}&{filter}.key={filter_key}&{filter}.displayName={display_name}"

            range_filter = ""
            if filter_from and filter_to:
                range_filter = {
                    "range": {
                        filter: {
                            "gte": filter_from,
                            "lt": filter_to
                        }
                    }
                }
            elif filter_from:
                range_filter = {
                    "range": {
                        filter: {
                            "gte": filter_from
                        }
                    }
                }
            filters.append(range_filter)

        ## FILTER TYPE == TERMS ########################################################
        elif type == "terms":
            display_filters.append(f"filter.name={filter}, type={type}, key={filter_key}")
            applied_filters += f"&filter.name={filter}&{filter}.type={type}&{filter}.key={filter_key}&{filter}.displayName={display_name}"
            terms_filter = {"term": {filter + ".keyword": filter_key} }
            filters.append(terms_filter)

    print("Filters post-process: {}".format(filters))
    return filters, display_filters, applied_filters


# Our main query route.  Accepts POST (via the Search box) and GETs via the clicks on aggregations/facets
@bp.route('/query', methods=['GET', 'POST'])
def query():
    opensearch = get_opensearch() # Load up our OpenSearch client from the opensearch.py file.
    # Put in your code to query opensearch.  Set error as appropriate.
    error = None
    user_query = None
    query_obj = None
    display_filters = None
    applied_filters = ""
    filters = None
    sort = "_score"
    sortDir = "desc"
    if request.method == 'POST':  # a query has been submitted
        user_query = request.form['query']
        if not user_query:
            user_query = "*"
        sort = request.form["sort"]
        if not sort:
            sort = "_score"
        sortDir = request.form["sortDir"]
        if not sortDir:
            sortDir = "desc"
        query_obj = create_query(user_query, [], sort, sortDir)
    elif request.method == 'GET':  # Handle the case where there is no query or just loading the page
        user_query = request.args.get("query", "*")
        filters_input = request.args.getlist("filter.name")
        sort = request.args.get("sort", sort)
        sortDir = request.args.get("sortDir", sortDir)
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)

        query_obj = create_query(user_query, filters, sort, sortDir)
    else:
        query_obj = create_query("*", [], sort, sortDir)

    # CALL TO OPENSEARCH
    print("query obj: {}".format(query_obj))
    response =  opensearch.search(
        body = query_obj,
        index = INDEX_NAME
    )
    #print(response)
    # Postprocess results here if you so desire

    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir)
    else:
        redirect(url_for("index"))


def create_query(user_query, filters, sort="_score", sortDir="desc"):
    print("Query: {} Filters: {} Sort: {}".format(user_query, filters, sort))
    base_query = {
        "multi_match": {
            "query": user_query,
            "fields": ["name^1000", "shortDescription^50", "longDescription^10", "department"]
        }
    }

    if user_query == '*':
        base_query = {
            "match_all": {}
        }

    query_obj = {
        "size": 10,
        ## QUERY
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [base_query],
                        "filter": filters
                    }
                },
                ## BOOSTER
                "boost_mode": "replace",  # multiply
                "score_mode": "avg",
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "salesRankLongTerm",
                            "missing": 100000000,
                            "modifier": "reciprocal"
                        }
                    },
                    {
                        "field_value_factor": {
                            "field": "salesRankMediumTerm",
                            "missing": 100000000,
                            "modifier": "reciprocal"
                        }
                    },
                    {
                        "field_value_factor": {
                            "field": "salesRankShortTerm",
                            "missing": 100000000,
                            "modifier": "reciprocal"
                        }
                    },
                ]
            }
        },
        ## SORT
        "sort": [
            {sort: {"order": sortDir}}
        ],
        ## AGGREGATE
        "aggs": {
            "departments": {
                "terms": {
                    "field": "department.keyword",
                    "size": 10
                }
            },
            "regularPrice": {
                "range": {
                    "field": "regularPrice",
                    "ranges": [
                        {"from": 0, "to": 49},
                        {"from": 50, "to": 99},
                        {"from": 100, "to": 250},
                        {"from": 250}
                    ]
                }
            },
            "missing_images": {
                "missing": {
                    "field": "image"
                }
            }
        },
        "_source": ["productId", "name", "shortDescription", "longDescription", "department", "salesRankShortTerm",  "salesRankMediumTerm", "salesRankLongTerm", "regularPrice"]
    }

    return query_obj


     