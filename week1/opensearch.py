import os
from dotenv import load_dotenv
from flask import g, current_app
from opensearchpy import OpenSearch

HOST = 'localhost'
PORT = 9200

# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    if "opensearch" not in g:
        # Implement a client connection to OpenSearch so that the rest of the application can communicate with OpenSearch

        # load_dotenv()

        # auth = (
        #     os.environ.get("OPENSEARCH_USERNAME", None),
        #     os.environ.get("OPENSEARCH_PW", None),
        # )

        auth = ('admin', 'admin')

        # Create the client with SSL/TLS disabled, and hostname verification disabled.
        openSearchClient = OpenSearch(
            hosts=[{"host": HOST, "port": PORT}],
            http_compress=True, 
            http_auth=auth,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

        g.opensearch = openSearchClient

    return g.opensearch

