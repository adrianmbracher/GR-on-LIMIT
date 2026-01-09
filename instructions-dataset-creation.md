# Instructions Dataset Creation
This is an instruction on how we modify the ![LIMIT benchmark](https://github.com/google-deepmind/limit) by Weller et al.


## Formatting LIMIT <a name="formatting_limit"></a>
1. `mkdir data`
2. `cd data`
3. download `queries.jsonl`, `corpus.jsonl` and `qrels.jsonl` from the ![LIMIT repository](https://github.com/google-deepmind/limit)
4. run `python to_seal_fmi_format.py` to create `nq-dev.json`
5. run `python build_raw_tsv.py` to create `raw.tsv`
6. (optional) `rm queries.jsonl`,  `rm corpus.jsonl`,  `rm qrels.jsonl` as they are no longer needed



## LIMIT-H
1. start with `nq-dev.json` and `raw.tsv` (see ![Formatting LIMIT](##formatting_limit) in the working directory
2. create hard documents with `python add_hard_documents.py` (make sure that paths match your local file structure)
3. run `python remove_newlines.py` to clean the output
4. append hard documents to original documents by running `cat raw.tsv raw-hard.tsv > raw.tsv` 
5. run `python check_hard_documents.py` (make sure that paths match your local file structure)


## LIMIT-HS
1. 
