import os
import json
import pickle
from inverted_index_gcp import InvertedIndex
from inverted_index_gcp import get_bucket
from inverted_index_gcp import _open

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "peaceful-garden-413921-1be5a48a52d4.json"

PROJECT_ID = 'peaceful-garden-413921'

# Put your bucket name below
bucket_name = '209502079'
bucket = get_bucket(bucket_name)


# Load title index
title_index = InvertedIndex.read_index("title_index", "index_for_title", bucket_name)

# Load body index
body_index = InvertedIndex.read_index("body_index", "index_for_body", bucket_name)

# Load pagerank dict
pagerank_blob_path = "pagerank_dict.pkl"
with _open(pagerank_blob_path, 'rb', bucket) as f:
    pagerank_dict = pickle.load(f)

# Load document lengths
document_lengths_blob_path = "document_lengths.pkl"
with _open(document_lengths_blob_path, 'rb', bucket) as f:
    document_lengths = pickle.load(f)

# Load title lengths
title_lengths_blob_path = "title_lengths.pkl"
with _open(title_lengths_blob_path, 'rb', bucket) as f:
    title_lengths = pickle.load(f)

# Load id_to_title_dict
id_to_title_dict_blob_path = "id_to_title_dict.pkl"
with _open(id_to_title_dict_blob_path, 'rb', bucket) as f:
    id_to_title_dict = pickle.load(f)


train_dict_blob_path = "queries_train.json"
with _open(train_dict_blob_path, 'rb', bucket) as f:
    train_dict = json.load(f)

