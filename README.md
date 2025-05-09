# Jupyter Notebook Best Practices Validator

This tool aims at validating the notebooks against the [CEOS Jupyter Notebook Best Practice v1.1](https://ceos.org/document_management/Working_Groups/WGISS/Documents/WGISS%20Best%20Practices/CEOS_JupterNotebooks_Best%20Practice_v1.1.pdf) document.

In its current implementation, the tool verifies whether a given Jupyter Notebook contains properties defined as mandatory or recommended in different specifications.

The tool takes as input the name of the "schema" (`eumetsat` or `schema.org`) and checks the presence of mandatory and optional properties. The specifications are based on the content of the [Appendix C of the BP document](https://github.com/ceos-org/jupyter-best-practice/blob/main/annex/annex-c.md).

## How it works

The tool uses the [`jsonschema`](https://python-jsonschema.readthedocs.io/en/stable/) Python library to validate the `metadata` section of each notebook against a custom schema provided in a local JSON file.

The validator is capable of dynamically resolving references to external schema definitions using the [`referencing`](https://referencing.readthedocs.io/en/stable/) library. This is needed for the `schema.org` option which requires the use of resources from the repository [SpaceApps/schema-org-json-schemas](https://github.com/SpaceApps/schema-org-json-schemas), which converts [schema.org](https://schema.org/) classes into JSON Schema format.

## Output

As the tool can handle multiple notebooks at once, the output is a list of JSON objects, one per notebook analyzed.

Each object contains:
- The name of the file.
- The schema used for validation.
- A list of missing required fields (empty if none are missing).
- A list of missing optional fields (optional, only present if any are missing).
- A list of JSON Schema validation errors (optional, only if errors were raised).

## Install

```sh
pip install .
```

## CLI
```
usage: nb-validator [-h] -s SCHEMA [-p] files [files ...]

Validate Jupyter notebooks metadata against a JSON schema.

positional arguments:
  files                 Paths to .ipynb files to validate.

options:
  -h, --help            show this help message and exit
  -s SCHEMA, --schema SCHEMA
                        Supported values: 'eumetsat' or 'schema.org'.
  -p, --abspath         Uses absolute paths in output.```
