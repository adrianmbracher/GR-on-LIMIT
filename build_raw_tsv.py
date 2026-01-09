import json


#INPUT = "./limit/limit-custom/corpus.jsonl"
INPUT = "./limit/limit/corpus.jsonl"
OUTPUT = "./limit_formatted/limit_seal/raw.tsv"

if __name__ == "__main__":
    with open(INPUT, "r") as input_file, open(OUTPUT, "w") as output_file:
        for line in input_file:
            doc = json.loads(line)
            output_file.write(f"{doc['_id']}\t{doc['title']}\t{doc['text']}\t\n")

