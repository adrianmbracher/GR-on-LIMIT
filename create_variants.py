
import os

LIMIT_PATH = "./limit"


if __name__ == "__main__":
    original_verb = "likes"
    verbs = ["touches", "owns", "likes"]

    for verb in verbs:
        new_path = f'{LIMIT_PATH}_{verb}'
        os.mkdir(new_path)
        for file in ["nq-dev.json", "raw.tsv"]:
            with (open(f"{LIMIT_PATH}/{file}", "r") as in_file,
                open(f"{new_path}/{file}", "w") as out_file):
                txt = in_file.read()
                txt = txt.replace(f" {original_verb} ", f" {verb} ")
                out_file.write(txt)


