import json
import urllib.request
import os

LIMIT_PATH = "./limit"
RAW_REPO_PATH = "https://raw.githubusercontent.com/google-deepmind/limit/refs/heads/main/data/limit"
QUERIES_PATH = f"{LIMIT_PATH}/queries.jsonl"
CORPUS_PATH = f"{LIMIT_PATH}/corpus.jsonl"
QRELS_PATH = f"{LIMIT_PATH}/qrels.jsonl"
NQ_DEV_JSON_PATH = f"{LIMIT_PATH}/nq-dev.json"
RAW_TSV_PATH = f"{LIMIT_PATH}/raw.tsv"


def create_nq_dev(q_file, o_file):
    res = []
    i = 0
    for query_line in q_file:
        i += 1
        print(f"Progress: {i}/1000")
        query = json.loads(query_line)
        positive_ctxs = []
        negative_ctxs = []
        hard_negative_ctxs = []
        with open(QRELS_PATH, "r") as qrels_file:
            for qrel_line in qrels_file:
                qrel = json.loads(qrel_line)
                if qrel["query-id"] == query["_id"]:
                    with open(CORPUS_PATH, "r") as corpus_file:
                        for passage_line in corpus_file:
                            passage = json.loads(passage_line)
                            if passage["_id"] == qrel["corpus-id"]:
                                ctx = {
                                    "title": passage["title"],
                                    "text": passage["text"],
                                    "score": qrel["score"],
                                    "title_score": qrel["score"],
                                    "passage_id": qrel["corpus-id"]
                                }
                                if qrel["score"] == 1:
                                    positive_ctxs.append(ctx)
                                elif qrel["score"] < 0:
                                    negative_ctxs.append(ctx)
        res.append({
            "dataset": "limit",
            "question": query["text"],
            "answers": [i["passage_id"] for i in positive_ctxs],
            "positive_ctxs": positive_ctxs,
            "negative_ctxs": negative_ctxs,
            "hard_negative_ctxs": hard_negative_ctxs,
        })
    o_file.write(json.dumps(res))




if __name__ == "__main__":
    print("Creating folder ...")
    os.mkdir(LIMIT_PATH)
    print("Downloading files ...")
    urllib.request.urlretrieve(f"{RAW_REPO_PATH}/corpus.jsonl", CORPUS_PATH)
    urllib.request.urlretrieve(f"{RAW_REPO_PATH}/qrels.jsonl", QRELS_PATH)
    urllib.request.urlretrieve(f"{RAW_REPO_PATH}/queries.jsonl", QUERIES_PATH)

    print("Creating nq_dev.json ...")
    # Convert limit queries to DPR format
    with (open(QUERIES_PATH, "r") as dev_queries_file,
          open(NQ_DEV_JSON_PATH, "w") as dev_output_file
          ):
        create_nq_dev(dev_queries_file, dev_output_file)

    print("Creating raw.tsv ...")
    with open(CORPUS_PATH, "r") as input_file, open(RAW_TSV_PATH, "w") as output_file:
        for line in input_file:
            doc = json.loads(line)
            output_file.write(f"{doc['_id']}\t{doc['title']}\t{doc['text']}\t\n")
