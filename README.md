# Generative Retrieval Overcomes Limitations of Dense Retrieval but Struggles with Identifier Ambiguity

## Instructions Dataset Creation
This is an instruction on how we modify the [LIMIT benchmark](https://github.com/google-deepmind/limit) by Weller et al.

### Formatting LIMIT <a name="formatting_limit"></a>
1. Download the dataset and convert to DPR format: `python download_and_convert.py`
2. Create three variants that differ only in relation by changing the verb ('likes', 'owns', 'touches'): `python create_variants.py`

### LIMIT-H <a name="limit-h"></a>
1. create -h datasets by enriching negative documents with `python enrich_negatives.py`

### LIMIT-HS <a name="limit-hs"></a>
1. create -hs datasets by duplicating negatives with `python duplicate_negatives.py`

## Generating Pseudo-Queries
Run `python create_pid2query_docT5query.py` and `python create_pid2query_oracle.py` to generate the pseudo-queries for the DT5Q and Oracle configurations respectively.

## SEAL Configurations

We apply the classical beam search algorithm during decoding in the second configuration. This requires us to adapt the `fm_index_generate` method in `beam_search.py` by setting `keep_history=False` and `unigram_scorest=None` in the `aggregate_evidence` method in `keys.py`.

| Configuration  | Parameters                                 |
|:---------------|:-------------------------------------------|
| (1) Default    | (default)                                  |
| (2) BEAM       | `keep_history=False` `unigram_scores=None` |


## MINDER Configurations

The adaptations regarding classical beam search decoding are as for SEAL in configurations 2-4. Identifiers are set by computing the corresponding FM-Index based on the used pseudo-query files, and setting the `--decode_query` parameter. 

| Configuration     | Parameters                                                         |
|:------------------|:-------------------------------------------------------------------|
| (1) NG+DT5Q       | `--decode_query stable`                                            |
| (2) NG; BEAM      | `keep_history=False` `unigram_scores=None`                         |
| (3) NG+DT5Q; BEAM | `keep_history=False` `unigram_scores=None` `--decode_query stable` |
| (4) Oracle        | `keep_history=False` `unigram_scores=None` `--decode_query stable` |


## Inference

First, the FM-Index must be generated (in the case of MINDER dependent on the identifier selection):

```
python scripts/build_fm_index.py \
    "${DATA_SRC}/raw.tsv" "${FMINDEX}" \
    --hf_model ... \
    --pid2query "${DATA_SRC}/pseudo_queries/pid2query.pkl" \
    --include_query
```


SEAL can be run as follows, for more details see the [SEAL repository](https://github.com/facebookresearch/SEAL)
```
python -m seal.search --topics_format dpr \
    --topics "${DATA_SRC}/nq-dev.json"     \
    --checkpoint data_dpr/SEAL-checkpoint+index.NQ/SEAL.NQ.pt \
    --output_format dpr \
    --output "output.json" \
    --fm_index "${FMINDEX}"  \
    --jobs 75 --progress --device cuda:0 --batch_size 1  --beam 10 
```

MINDER can be run as follows, for more details see the [MINDER repository](https://github.com/liyongqi67/MINDER)
```
python -m seal.search --topics_format dpr \
    --topics "${DATA_SRC}/nq-dev.json" \
    --output_format dpr \
    --output "output.json" \
    --checkpoint checkpoint_NQ.pt \
    --jobs 10 --progress --device cuda:0 --batch_size 20 --beam 15 \
    --fm_index "${FMINDEX}" \
    --decode_query stable 
```

BM25 was run via Pyserini, which requires a different format - to parse the data run `python convert_data_to_pyserini.py -in "${DATA_SRC}" -out "${PYSERINI_DATA}"`. Next, the BM25 index is created via 
```
python -m pyserini.index.lucene   \
  --collection JsonCollection   \
  --input "${PYSERINI_DATA}"   \
  --index "${INDEX_SRC}"  \
  --generator DefaultLuceneDocumentGenerator   --threads 1   --storePositions --storeDocvectors --storeRaw
```

And finally, search using: 
```
python bm25search.py -in "${DATA_SRC}" -out "output_bm25_${PREFIX}" --index "${INDEX_SRC}"
```

    

