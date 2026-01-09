import json
import prompts

from pydantic import BaseModel
from ollama import chat
from ollama import ChatResponse



#TRAINING_INPUT = "./limit_formatted/limit_seal/nq-train.json"
DEV_INPUT = "./data/nq-dev.json"
#TRAINING_OUTPUT = "./limit_formatted/limit_seal/nq-train-hard.json"
DEV_OUTPUT = "./data/nq-dev-hard.json"
HARD_TSV = "./data/raw-hard.tsv"

class Response(BaseModel):
    finalanswer: str

def enrich_hard_documents(input, hard_doc_dict):
    for query in input:
        negative_ctxs = []
        for positive_ctx in query["positive_ctxs"]:
            if positive_ctx["passage_id"] in hard_doc_dict:
                negative_ctxs.append(hard_doc_dict.get(positive_ctx["passage_id"]))
        query["negative_ctxs"] += negative_ctxs
    return input

def collect_documents(input):
    docs = []
    docids = set()
    for query in input:
        for positive_ctx in query["positive_ctxs"]:
            if positive_ctx["passage_id"] not in docids:
                docs.append(positive_ctx)
                docids.add(positive_ctx["passage_id"])
    return docs

def create_hard_doc_dict(original_documents):
    hard_doc_dict = {}
    for doc in original_documents:
        res = None
        while res is None:
            print("> " + doc["text"])
            response: ChatResponse = chat(model='deepseek-r1:70b', messages=[
                {
                    'role': 'user',
                    'format': Response.model_json_schema(),
                    'content': f"{prompts.hard_doc_query} '{doc['text']}'\n"
                }])
            res = response["message"]["content"]
            if res.find('</think>') != -1:
                res = res.split('</think>')[1]
            # for item in positive_ctx["text"].split("likes ")[1].replace(" and ", ", ").split(", "):
            #    if res.find(item) == -1:
            #        print(f"{item} not found in {res}")
            #        res = None
            #        break
            if res is not None and res.find(doc["text"]) != -1:
                res = None
                print("entire original text preserved")

        ctx = {
            "title": "n_" + doc["title"],
            "text": res,
            "score": 0,
            "title_score": 0,
            "passage_id": "n_" + doc["passage_id"]
        }
        with open(HARD_TSV, "a") as raw_hard_doc_file:
            raw_hard_doc_file.write(f"{ctx['passage_id']}\t{ctx['title']}\t{ctx['text']}\t\n")
        hard_doc_dict.update({doc["passage_id"]: ctx})
    return hard_doc_dict

if __name__ == "__main__":
    with (#open(TRAINING_INPUT, "r") as training_input_file,
          #open(TRAINING_OUTPUT, "w") as training_output_file,
          open(DEV_INPUT, "r") as dev_input_file,
          open(DEV_OUTPUT, "w") as dev_output_file,
          ):
        dev_input = json.load(dev_input_file)
        print("collecting documents ...")
        documents = collect_documents(dev_input)
        print("creating hard document dictionary ...")
        hard_documents_dict = create_hard_doc_dict(documents)
        print("enriching hard documents in corpus")
        dev_output = enrich_hard_documents(dev_input, hard_documents_dict)
        json.dump(dev_output, dev_output_file)
