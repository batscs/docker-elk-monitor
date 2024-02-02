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

        print(self.elastic_documents)

        response = helpers.bulk(self.client, self.elastic_documents)

        # Dividing all data into smaller chunks
        # max_elements * 2, because every data record consists of two array-elements (see elastic_append_data)
        # chunks = array_divide_chunks(self.elastic_documents, self.elastic_bulk_max_elements * 2)

        if self.connect and False:
            for (index, chunk) in enumerate(chunks):
                # ElasticSearch Bulk API Communication (Sending of the Data)
                # response = self.client.bulk(operations=chunk)

                # Printing of the Response
                print(str(index + 1) + ". ElasticSearch Response -> Errors: " + str(
                    response["errors"]) + ", Items: " + str(
                    len(response["items"])))

                # Debug-Printing of entire response
                if self.debug: print(response)

        # Clear Documents
        self.elastic_documents = []
