import os

import torch
import pickle
from transformers import T5Tokenizer, T5ForConditionalGeneration

DATA_PATH = "./limit"
VERBS = ['likes', 'owns', 'touches']

# prepare docT5query model
model_path = "<PLACEHOLDER>"
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tokenizer = T5Tokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path)
model.to(device)

def create_pid2query_docT5query(initial_pid2query, input_tsv):
    pid2query = {}
    with open(input_tsv, 'r') as f:
        raw = f.readlines()
        line_no = -1
        len_lines = len(raw)
        for line in raw:
            line_no += 1
            docid, title, text = line.strip().split("\t")
            print(f"{line_no}/{len_lines}")

            if docid in initial_pid2query:
                pid2query[docid] = initial_pid2query[docid]
            else:
                input_ids = tokenizer.encode(text, return_tensors='pt').to(device)
                outputs = model.generate(
                    input_ids=input_ids,
                    max_length=64,
                    do_sample=True,
                    top_k=100,
                    num_return_sequences=50)
                queries = []

                for i in range(50):
                    queries.append(tokenizer.decode(outputs[i], skip_special_tokens=True).replace("?", ""))
                pid2query[docid] = queries
    return pid2query


if __name__ == "__main__":

    for verb in VERBS:

        # limit
        pid2query = create_pid2query_docT5query({}, f"{DATA_PATH}_{verb}/raw.tsv")
        os.makedirs(f"{DATA_PATH}_{verb}/pseudo_queries", exist_ok=True)
        with open(f"{DATA_PATH}_{verb}/pseudo_queries/pid2query-dt5q.pkl", 'wb') as g:
            pickle.dump(pid2query, g)

        # limit-h
        pid2query = create_pid2query_docT5query(pid2query, f"{DATA_PATH}_{verb}-h/raw.tsv")
        os.makedirs(f"{DATA_PATH}_{verb}-h/pseudo_queries", exist_ok=True)
        with open(f"{DATA_PATH}_{verb}-h/pseudo_queries/pid2query-dt5q.pkl", 'wb') as g:
            pickle.dump(pid2query, g)

        # limit-hs
        with open(f"{DATA_PATH}_{verb}-hs/raw.tsv", 'r') as f:
            raw = f.readlines()
            for line in raw:
                docid, title, text = line.strip().split("\t")
                if docid in pid2query:
                    continue

                assert docid[:3] == "n2_"
                queries = pid2query["n_" + docid[3:]]
                pid2query[docid] = queries
        os.makedirs(f"{DATA_PATH}_{verb}-hs/pseudo_queries", exist_ok=True)
        with open(f"{DATA_PATH}_{verb}-hs/pseudo_queries/pid2query-dt5q.pkl", 'wb') as g:
            pickle.dump(pid2query, g)





