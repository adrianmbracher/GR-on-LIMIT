
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == "__main__":
    with open("./limit_formatted/limit_seal/raw-hard.tsv", "r") as f, open("./limit_formatted/limit_seal/raw-hard-2.tsv", "w") as g:
        for lines in chunks(list(f), 3):
            new_record = f"{lines[0][:-1]}{lines[2]}"
            #print(repr(new_record))
            g.write(new_record)

