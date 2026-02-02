import json
import os
import pickle

from pydantic import BaseModel
from ollama import chat
from ollama import ChatResponse
import prompts

DATA_PATH = "./limit"
VERBS = ['likes', 'owns', 'touches']

class Response(BaseModel):
    finalanswer: str

def create_perfect_pseudo_queries(input_tsv, verb):
    pid2query = {}
    with open(input_tsv, 'r') as f:
        raw = f.readlines()
        for line in raw:
            docid, title, text = line.strip().split("\t")
            items = text.split(verb)[1].replace(" and ", ", ").split(", ")
            queries = [f"Who {verb}{item}?" for item in items]
            pid2query[docid] = queries
    return pid2query

def create_pseudo_queries_ollama(initial_pid2query, input_tsv, verb):
    prompt = prompts.pseudo_query_prompt
    if verb == "owns":
        prompt = prompts.pseudo_query_prompt_owns
    if verb == "touches":
        prompt = prompts.pseudo_query_prompt_touches

    pid2query = initial_pid2query
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
                res = None
                while res is None:
                    print("> " + text)
                    response: ChatResponse = chat(model='deepseek-r1:70b', messages=[
                        {
                            'role': 'user',
                            'format': Response.model_json_schema(),
                            'content': f"{prompt} {text}\n"
                        }])
                    res = response["message"]["content"]
                    if res.find('</think>') != -1:
                        res = res.split('</think>')[1]
                    res = res.replace("\n", "").split('[SEP]')
                    print(res)
                pid2query[docid] = res
    return pid2query



if __name__ == "__main__":

    for verb in VERBS:

        # limit
        print(f"{DATA_PATH}_{verb}")
        pid2query = create_perfect_pseudo_queries(f"{DATA_PATH}_{verb}/raw.tsv", verb)
        os.makedirs(f"{DATA_PATH}_{verb}/pseudo_queries", exist_ok=True)
        with open(f"{DATA_PATH}_{verb}/pseudo_queries/pid2query-ollama.pkl", 'wb') as g:
            pickle.dump(pid2query, g)

        # limit-h
        print(f"{DATA_PATH}_{verb}-h")
        pid2query = create_pseudo_queries_ollama(pid2query, f"{DATA_PATH}_{verb}-h/raw.tsv", verb)
        os.makedirs(f"{DATA_PATH}_{verb}-h/pseudo_queries", exist_ok=True)
        with open(f"{DATA_PATH}_{verb}-h/pseudo_queries/pid2query-ollama.pkl", 'wb') as g:
            pickle.dump(pid2query, g)

        # limit-hs
        print(f"{DATA_PATH}_{verb}-hs")
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
        with open(f"{DATA_PATH}_{verb}-hs/pseudo_queries/pid2query-ollama.pkl", 'wb') as g:
            pickle.dump(pid2query, g)





