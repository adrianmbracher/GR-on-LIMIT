import json
import prompts

from pydantic import BaseModel

from ollama import chat
from ollama import ChatResponse

#RELATION = "likes "
RELATION = "owns "

OUTPUT_TSV = "data/raw_2.tsv"
INPUT_TSV = "data/raw.tsv"


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

def collect_original_documents(input):
    docs = []
    docids = set()
    for query in input:
        for positive_ctx in query["positive_ctxs"]:
            if positive_ctx["passage_id"] not in docids:
                docs.append(positive_ctx)
                docids.add(positive_ctx["passage_id"])
    return docs


if __name__ == "__main__":
    with (open("%s" % INPUT_TSV, "r") as dev_input_file, open(OUTPUT_TSV, "w") as dev_output_file):
        documents = {}
        for doc_line in dev_input_file:
            doc = doc_line.split("\t")
            documents[doc[0]] = doc[2]

        item_c = 0
        nf_item_c = 0

        for doc_id in [i for i in documents.keys() if not i.startswith("n_")]:
            if "n_" + doc_id in documents.keys():
                hard_text = documents["n_" + doc_id]
                not_found_items = []
                original_items = documents[doc_id].split(RELATION)[1].replace(" and ", ", ").replace(".", "").split(", ")
                is_complete = False
                while not is_complete:
                    for item in original_items:
                        if hard_text.find(item) == -1:
                            not_found_items.append(item)
                    if len(not_found_items) == 0:
                        is_complete = True
                        documents["n_" + doc_id] = hard_text.replace("\"", "").replace("\n", "")
                    else:
                        response: ChatResponse = chat(model='deepseek-r1:70b', messages=[
                            {
                                'role': 'user',
                                'format': Response.model_json_schema(),
                                'content': f"{prompts.completion_query} '({hard_text},{not_found_items})'\n"
                            }])
                        res = response["message"]["content"]
                        if res.find('</think>') != -1:
                            res = res.split('</think>')[1]
                        print(hard_text)
                        print(not_found_items)
                        print(res)

                        hard_text = res
                        not_found_items = []
                dev_output_file.write(f"{doc_id}\t{doc_id}\t{documents['n_' + doc_id]}\t\n")
                item_c += len(original_items)
                nf_item_c += len(not_found_items)
                print(f"{not_found_items} not found in {hard_text}")
        print(f"% not found: {nf_item_c / item_c}")

