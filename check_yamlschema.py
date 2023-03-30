import argparse
import re

import jsonschema
import requests
import yaml


def load_yaml_documents(file_path):
    with open(file_path) as file:
        content = file.read()
        documents = content.split("---\n")
        yaml_documents = []
        for doc in documents:
            if doc.strip() != "":
                comment = None
                schema_url = None
                for line in doc.split("\n"):
                    if line.startswith("# yaml-language-server"):
                        comment = line
                        match = re.match(
                            r"# yaml-language-server: \$schema=(.*)$",
                            comment,
                            re.MULTILINE,
                        )
                        if match:
                            schema_url = match.group(1)
                        break
                doc_dict = {
                    "content": yaml.safe_load(doc),
                    "comment": comment,
                    "schema_url": schema_url,
                }
                yaml_documents.append(doc_dict)
    return yaml_documents


def download_schema(schema_url):
    response = requests.get(schema_url)
    response.raise_for_status()
    return response.json()


def validate_document(document, schema_url):
    schema = download_schema(schema_url)
    jsonschema.validate(instance=document, schema=schema)
    print(f"Document validated according to {schema_url}")


def main():
    parser = argparse.ArgumentParser(description="Validate YAML document(s) against JSON schema.")
    parser.add_argument("file", type=str, help="Path to YAML file to validate")
    args = parser.parse_args()
    yaml_documents = load_yaml_documents(args.file)
    for doc in yaml_documents:
        if doc["schema_url"] is not None:
            validate_document(doc["content"], doc["schema_url"])


if __name__ == "__main__":
    main()
