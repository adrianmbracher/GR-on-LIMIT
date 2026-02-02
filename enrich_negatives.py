import json
import os
import prompts
from pydantic import BaseModel
from ollama import chat, ChatResponse

# --- Configuration ---
DATA_PATH = "./limit"
VERBS = ["likes", "owns", "touches"]

MODEL_NAME = 'deepseek-r1:70b'


class Response(BaseModel):
    finalanswer: str


def collect_unique_documents(input_data):
    """Extracts unique positive context documents from the input JSON."""
    docs = []
    docids = set()
    for query in input_data:
        for positive_ctx in query["positive_ctxs"]:
            if positive_ctx["passage_id"] not in docids:
                docs.append(positive_ctx)
                docids.add(positive_ctx["passage_id"])
    return docs


def extract_items_from_text(text, relation):
    """
    Parses the text to extract specific items based on the relation keyword.
    Logic adapted from check_hard_documents.py
    """
    if relation not in text:
        return []

    try:
        # Split by relation, take the second part, normalize separators
        content = text.split(relation)[1]
        content = content.replace(" and ", ", ").replace(".", "")
        items = [item.strip() for item in content.split(", ") if item.strip()]
        return items
    except IndexError:
        return []


def generate_initial_hard_doc(doc_text):
    """Generates the initial hard document using the LLM."""
    res = None
    while res is None:
        print(f"> Generating for: {doc_text[:50]}...")
        response: ChatResponse = chat(model=MODEL_NAME, messages=[
            {
                'role': 'user',
                'format': Response.model_json_schema(),
                'content': f"{prompts.hard_doc_query} '{doc_text}'\n"
            }])

        content = response["message"]["content"]

        # Clean thinking trace if present
        if '</think>' in content:
            content = content.split('</think>')[1].strip()

        # Validation: Ensure result is not identical to original
        if doc_text in content:
            print("  [Retry] Generated text contains entire original text.")
            res = None
        else:
            res = content

    return res


def ensure_completeness(original_text, hard_text, verb):
    """
    Iteratively fixes the hard_text until all items from original_text are present.
    """
    original_items = extract_items_from_text(original_text, verb)

    # If no items found or relation logic doesn't apply, skip verification
    if not original_items:
        return hard_text

    current_hard_text = hard_text
    is_complete = False

    while not is_complete:
        not_found_items = []
        for item in original_items:
            if item not in current_hard_text:
                not_found_items.append(item)

        if not not_found_items:
            is_complete = True
        else:
            print(f"  [Fixing] Missing items: {not_found_items}")
            response: ChatResponse = chat(model=MODEL_NAME, messages=[
                {
                    'role': 'user',
                    'format': Response.model_json_schema(),
                    # Assuming prompts.completion_query expects a tuple string format based on previous script
                    'content': f"{prompts.completion_query} '({current_hard_text},{not_found_items})'\n"
                }])

            res = response["message"]["content"]
            if '</think>' in res:
                res = res.split('</think>')[1].strip()

            current_hard_text = res

    # Clean up formatting (remove newlines/quotes) similar to original script
    return current_hard_text.replace("\"", "").replace("\n", " ")


def enrich_json_with_hard_docs(input_data, hard_doc_dict):
    """Adds the generated hard documents to the negative_ctxs of the original queries."""
    for query in input_data:
        negative_ctxs = []
        for positive_ctx in query["positive_ctxs"]:
            if positive_ctx["passage_id"] in hard_doc_dict:
                negative_ctxs.append(hard_doc_dict.get(positive_ctx["passage_id"]))
        query["negative_ctxs"] += negative_ctxs
    return input_data


def process_documents(documents, verb):
    """Main processing loop: Generate -> Verify -> Store"""
    hard_doc_dict = {}

    # Ensure directory exists for TSV
    os.makedirs(os.path.dirname(HARD_TSV), exist_ok=True)

    with open(HARD_TSV, "w") as raw_hard_doc_file:  # 'w' to overwrite, 'a' to append if running in batches
        for i, doc in enumerate(documents):
            print(f"Processing doc {i + 1}/{len(documents)}: {doc['passage_id']}")

            # Step 1: Generate Initial Hard Document
            hard_text = generate_initial_hard_doc(doc["text"])

            # Step 2: Verify and Fix (Check Hard Documents logic)
            final_hard_text = ensure_completeness(doc["text"], hard_text, verb)

            # Step 3: Create Context Object
            ctx = {
                "title": "n_" + doc["title"],
                "text": final_hard_text,
                "score": 0,
                "title_score": 0,
                "passage_id": "n_" + doc["passage_id"]
            }

            # Write to TSV immediately
            raw_hard_doc_file.write(f"{ctx['passage_id']}\t{ctx['title']}\t{ctx['text']}\t\n")
            raw_hard_doc_file.flush()  # Ensure write to disk

            # Update Dictionary
            hard_doc_dict[doc["passage_id"]] = ctx
        with open(TSV_IN, "r") as tsv_in:
            for og_doc in tsv_in:
                raw_hard_doc_file.write(og_doc)
                raw_hard_doc_file.flush()

    return hard_doc_dict


if __name__ == "__main__":
    for verb in VERBS:
        DEV_INPUT = f"{DATA_PATH}_{verb}/nq-dev.json"
        DEV_OUTPUT = f"{DATA_PATH}_{verb}-h/nq-dev.json"
        TSV_IN = f"{DATA_PATH}_{verb}/raw.tsv"
        HARD_TSV = f"{DATA_PATH}_{verb}-h/raw.tsv"
        print("Loading input data...")
        with open(DEV_INPUT, "r") as dev_input_file:
            dev_input = json.load(dev_input_file)

        print("Collecting unique documents...")
        unique_documents = collect_unique_documents(dev_input)

        print("Generating and verifying hard documents...")
        hard_documents_dict = process_documents(unique_documents, verb)

        print("Enriching original corpus...")
        dev_output = enrich_json_with_hard_docs(dev_input, hard_documents_dict)

        print(f"Saving enriched JSON to {DEV_OUTPUT}...")
        with open(DEV_OUTPUT, "w") as dev_output_file:
            json.dump(dev_output, dev_output_file, indent=2)

        print("Done.")
