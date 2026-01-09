import gzip
import json
import pickle

#QUERIES_PATH = "./limit/limit-custom/queries.jsonl"
QUERIES_PATH = "./limit/limit/queries.jsonl"
#TRAINING_QUERIES_PATH = "./limit/limit-custom/queries-train.jsonl"
#CORPUS_PATH = "./limit/limit-custom/corpus.jsonl"
CORPUS_PATH = "./limit/limit/corpus.jsonl"
#QRELS_PATH = "./limit/limit-custom/qrels.jsonl"
QRELS_PATH = "./limit/limit/qrels.jsonl"
#TRAINING_OUTPUT_PATH = "./limit_formatted/limit_seal/nq-train.json"
DEV_OUTPUT_PATH = "./limit_formatted/limit_seal/nq-dev.json"


def parse_queries(q_file, o_file):
    res = []
    i = 0
    for query_line in q_file:
        i += 1
        print(f"{i}")
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
            #"answers": [],
            "answers": [i["passage_id"] for i in positive_ctxs],
            #"positive_ctxs": [],
            "positive_ctxs": positive_ctxs,
            #"negative_ctxs": [],
            "negative_ctxs": negative_ctxs,
            #"hard_negative_ctxs": [],
            "hard_negative_ctxs": hard_negative_ctxs,
        })
    o_file.write(json.dumps(res))


if __name__ == "__main__":
    # Convert limit queries to msmarco tsv format
    with (#open(TRAINING_QUERIES_PATH, "r") as training_queries_file,
          open(QUERIES_PATH, "r") as dev_queries_file,
          #open(TRAINING_OUTPUT_PATH, "w") as training_output_file,
          open(DEV_OUTPUT_PATH, "w") as dev_output_file
          ):
        #parse_queries(training_queries_file, training_output_file)
        parse_queries(dev_queries_file, dev_output_file)
