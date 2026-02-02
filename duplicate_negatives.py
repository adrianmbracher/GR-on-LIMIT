import os
import shutil

DATA_PATH = "./limit"
VERBS = ["likes", "owns", "touches"]


def duplicate_n_lines(input_tsv, output_tsv):
    # Ensure the directory exists
    if not os.path.exists(input_tsv):
        print(f"Error: {input_tsv} not found.")
        return

    with open(input_tsv, "r", encoding="utf-8") as infile, \
            open(output_tsv, "w", encoding="utf-8") as outfile:

        count = 0
        duplicated_count = 0

        for line in infile:
            outfile.write(line)
            count += 1

            parts = line.split("\t", 1)

            if len(parts) > 0 and parts[0].startswith("n_"):
                line = line.replace("n_", "n2_")
                outfile.write(line)
                duplicated_count += 1

    print(f"Processing complete.")
    print(f"Total lines read: {count}")
    print(f"Lines duplicated (starting with 'n_'): {duplicated_count}")
    print(f"Output saved to: {output_tsv}")


if __name__ == "__main__":
    for verb in VERBS:
        input_tsv = f"{DATA_PATH}_{verb}-h/raw.tsv"
        output_tsv = f"{DATA_PATH}_{verb}-hs/raw.tsv"
        os.mkdir(f"{DATA_PATH}_{verb}-hs")
        shutil.copy(f"{DATA_PATH}_{verb}-h/nq-dev.json", f"{DATA_PATH}_{verb}-hs/nq-dev.json")
        duplicate_n_lines(input_tsv, output_tsv)
