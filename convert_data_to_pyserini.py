import argparse
import json
import os

def convert_to_pyserini_format(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_file = input_folder + "/raw.tsv"

    output_file = output_folder + '/documents.jsonl'

    print(f"Reading from {input_folder}/raw.tsv ...")

    with open(input_folder + "/readme.txt", "r") as readme_in, open(output_folder + "/readme.txt", "w") as readme_out:
        readme_out.writelines(readme_in.readlines())

    with open(input_file, 'r', encoding='utf-8') as f_in, \
            open(output_file, 'w', encoding='utf-8') as f_out:

        doc_count = 0
        for entry in f_in.readlines():
            pid, _, content = entry.replace('\t\n', "").split('\t')

            # Create the Pyserini document object
            doc = {
                "id": pid,
                "contents": content
            }

            f_out.write(json.dumps(doc) + '\n')
            doc_count += 1

    print(f"Successfully converted {doc_count} unique documents to {output_file}")

parser = argparse.ArgumentParser()
parser.add_argument('-in', '--input_folder', type=str, help='Input folder', default='data')
parser.add_argument('-out', '--output_folder', type=str, help='Output folder', default='pyserini_data_default')


if __name__ == "__main__":
    args = parser.parse_args()
    # Replace with your actual file name
    convert_to_pyserini_format(args.input_folder, args.output_folder)
