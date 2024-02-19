# ElasticSearch Interface
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from datetime import datetime
from datetime import timezone

class ElasticAPI:
    def __init__(self, elastic_domain, elastic_api_key, elastic_index_name, debug=False, connect=True,
                 max_elements=500):
        self.elastic_documents = []
        self.elastic_index_name = elastic_index_name

        self.debug = debug
        self.connect = connect

        self.elastic_index_cleanup = True

        if self.connect: self.client = Elasticsearch(
            elastic_domain,
            api_key=elastic_api_key,
            verify_certs=False,  # False, otherwise provide a valid certificate
        )

        self.elastic_bulk_max_elements = max_elements

    # Function to append a processed log to the document for ElasticSearch
    def append_data(self, field_record, timestamp=""):

        if timestamp == "":
            timestamp = datetime.now(timezone.utc).isoformat()

        field_record["@timestamp"] = timestamp

        action = {
            "_index": self.elastic_index_name,
            "_source": field_record
        }

        self.elastic_documents.append(action)

        # Required to append data to already existing index for ElasticSearch
        # self.elastic_documents.append({"index": {"_index": self.elastic_index_name}})

        # Data to append
        # self.elastic_documents.append(field_record)

        # Debug-Printing
        if self.debug: print(action)
        if self.debug: print("")

    # Function to send all processed data to ElasticSearch in small chunks and get
    # information about errors and item count
    def submit_data(self):

        if not self.client.indices.exists(index=self.elastic_index_name):
            print("Elastic Index does not exist, trying to create.")
            self.client.indices.create(index=self.elastic_index_name)

        # print(self.elastic_documents)

        # Upload Fetched Data
        response = helpers.bulk(self.client, self.elastic_documents)

        print(response)

        # Remove Data from Index older than 2 days.
        if self.elastic_index_cleanup: response = self.client.delete_by_query(
            index=self.elastic_index_name,
            body={"query": {"range": {"@timestamp": { "lte": "now-2d" }}}},
        )

        # Clear Documents
        self.elastic_documents = []
