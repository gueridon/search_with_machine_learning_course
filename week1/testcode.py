import os
from dotenv import load_dotenv
from opensearchpy import OpenSearch

HOST = 'localhost'
PORT = 9200

# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    load_dotenv()

    auth = (
        os.environ.get("OPENSEARCH_USERNAME", None),
        os.environ.get("OPENSEARCH_PW", None),
    )
    print("hello")

    openSearchClient = OpenSearch(
                                    hosts = [{'host': HOST, 'port': PORT}],
                                    http_compress = True,
                                    http_auth = auth,
                                    use_ssl = True,
                                    verify_certs = False,
                                    ssl_assert_hostname = False,
                                    ssl_show_warn = False,)
    
    return openSearchClient

client = get_opensearch()


