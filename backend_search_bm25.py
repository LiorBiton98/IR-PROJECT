# import nltk
from collections import defaultdict
from nltk.stem.porter import *
from nltk.corpus import stopwords
import math
from files import title_index, body_index, pagerank_dict, document_lengths, title_lengths, id_to_title_dict

# nltk.download('stopwords')

english_stopwords = frozenset(stopwords.words('english'))
corpus_stopwords = ["category", "references", "also", "external", "links",
                    "may", "first", "see", "history", "people", "one", "two",
                    "part", "thumb", "including", "second", "following",
                    "many", "however", "would", "became"]

all_stopwords = english_stopwords.union(corpus_stopwords)
RE_WORD = re.compile(r"""[\#\@\w](['\-]?\w){2,24}""", re.UNICODE)


def process_query(query):
    # Tokenize the query
    query_tokens = [token.group() for token in RE_WORD.finditer(query.lower())]

    # Remove stopwords from the query
    query_tokens = [token for token in query_tokens if token not in all_stopwords]

    return query_tokens


def bm25_score_combined(query, body_index, title_index, folder_name,document_lengths, title_lengths, bucket_name = '209502079', k1=1.5, k3=0, b=0.75):
    scores = defaultdict(float)
    total_docs = len(document_lengths)
    total_title_docs = len(title_lengths)

    # Calculate average document length for body
    sum_body_length = 0
    for length in document_lengths.values():
        sum_body_length += length
    avg_body_length = sum_body_length / total_docs

    # Calculate average document length for title
    sum_title_length = 0
    for length in title_lengths.values():
        sum_title_length += length
    avg_title_length = sum_title_length / total_title_docs

    tfiq = {term: 1 for term in query}

    for term in query:
        # Calculate IDF for body
        body_posting_list = body_index.read_a_posting_list(folder_name, term, bucket_name)
        body_df = len(body_posting_list)
        if body_df == 0:
          body_idf = 0
        else:
          body_idf = math.log((total_docs + 1) / body_df)

        # Calculate BM25 score for body
        for doc_id, tf in body_posting_list:
            if len(query) < 3:
                continue
            else:
                body_length = document_lengths[doc_id]
                B = 1 - b + b * (body_length / avg_body_length)
                tf_normalized = tf * (k1 + 1) / (tf + k1 * B)
                tfiq_normalized = (k3 + 1) * tfiq[term] / (k3 + tfiq[term])
                scores[doc_id] += 0.3*(body_idf * tf_normalized * tfiq_normalized)

    for term in query:
        # Calculate IDF for title
        title_posting_list = title_index.read_a_posting_list(folder_name, term, bucket_name)
        title_df = len(title_posting_list)
        if title_df == 0:
          title_idf = 0
        else:
          title_idf = math.log((total_title_docs + 1) / title_df)

        # Calculate BM25 score for title
        for doc_id, tf in title_posting_list:
            title_length = title_lengths[doc_id]
            B = 1 - b + b * (title_length / avg_title_length)
            tf_normalized = tf * (k1 + 1) / (tf + k1 * B)
            tfiq_normalized = (k3 + 1) * tfiq[term] / (k3 + tfiq[term])
            if len(query) < 3:
                scores[doc_id] += title_idf * tf_normalized * tfiq_normalized
            else:
                scores[doc_id] += 0.7*(title_idf * tf_normalized * tfiq_normalized)

    sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
    return sorted_scores


def retrieval_function_bm25(query, index_body, index_title, folder_name, document_lengths, title_lengths, pagerank_scores, id_to_title_dict, bucket_name = '209502079'):
    # Calculate BM25 scores
    bm25_scores = bm25_score_combined(query, index_body, index_title, folder_name, document_lengths, title_lengths, bucket_name, k1=1.5, k3=0, b=0.75)

    # Combine BM25 scores and PageRank scores
    combined_scores = defaultdict(float)
    count = 0
    for doc_id, bm25_score in bm25_scores.items():
        if count >= 30:
            break
        pagerank_score = pagerank_scores[doc_id]
        combined_scores[doc_id] = 1 * 1000 * bm25_score + 5 * pagerank_score
        count += 1
    # Rank documents based on combined scores
    ranked_documents = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

    # Retrieve up to 30 search results with titles
    search_results = []
    for doc_id, score in ranked_documents:
        title = id_to_title_dict.get(doc_id, "Title not available")
        search_results.append((str(doc_id), title))

    return search_results


def backend_search_bm25(query):
    # Process the query
    query = process_query(query)

    # Retrieve search results using the retrieval function
    search_results = retrieval_function_bm25(query, body_index, title_index, '.', document_lengths, title_lengths,
                                         pagerank_dict, id_to_title_dict, bucket_name='209502079')

    return search_results

