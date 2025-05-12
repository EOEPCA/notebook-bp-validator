#!/usr/bin/env python3

import os
import re
import sys
import json
import urllib.request
import importlib.resources

from jsonschema import Draft7Validator
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from nb_validator import schemas

def _add_schema_org_schema_to_registry(schema_name: str, registry: Registry) -> Registry:
    print(f"Adding '{schema_name}' to registry", file=sys.stderr)
    with urllib.request.urlopen(f"https://raw.githubusercontent.com/SpaceApplications/schema-org-json-schemas/refs/heads/master/schemas/{schema_name}.schema.json") as response:
        schema = json.load(response)

    return registry.with_resource(f"schema:{schema_name}", Resource.from_contents(schema))

def _init_registry_with_string_types() -> Registry:
    string_type = Resource.from_contents(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "string",
        }
    )
    resources = [
        ("schema:Text", string_type),
        ("schema:URL", string_type)  # because "URL" schema has type "object", oddly
    ]
    registry = Registry().with_resources(resources)

    return registry

def validate_notebook(
    notebook_path: str,
    encoding: str,
    # registry: Registry,
    abspath: bool
) -> dict:
    result = {
        "filename": os.path.abspath(notebook_path)
                        if abspath
                        else os.path.relpath(notebook_path, os.path.curdir),
        "schema": encoding
    }

    try:
        with open(notebook_path) as f:
            notebook = json.load(f)
    except Exception as e:
        result["error"] = f"Error reading notebook file: {e}"
        return result

    if "metadata" not in notebook:
        result["error"] = "Notebook does not contain a 'metadata' section."
        return result

    metadata = notebook["metadata"]

    if encoding.lower() == "eumetsat":
        with importlib.resources.files(schemas).joinpath("eumetsat.schema.json").open("r") as f:
            schema = json.load(f)
        validator = Draft7Validator(schema)
        errors = sorted(validator.iter_errors(metadata), key=lambda e: e.path)  # returns an Iterable of ValidationErrors
    elif encoding.lower() == "schema.org":
        # if not registry:
        registry = _init_registry_with_string_types()
        with importlib.resources.files(schemas).joinpath("schema_org.schema.json").open("r") as f:
            schema = json.load(f)
        while True:
            try:
                validator = Draft7Validator(schema, registry=registry)
                errors = sorted(validator.iter_errors(metadata), key=lambda e: e.path)  # returns an Iterable of ValidationErrors
                break
            except Unresolvable as e:
                match = re.search(r"schema:([A-Za-z]+)", str(e))
                schema_name = match.group(1) if match else None
                print(f"[{os.path.basename(notebook_path)}] Unresolved schema '{schema_name}'", file=sys.stderr)
                registry = _add_schema_org_schema_to_registry(schema_name, registry)
    else:
        result["error"] = f"Unknown encoding type: {encoding}"
        return result

    missing_mandatory_fields = []
    validation_errors = []

    for err in errors:
        if err.validator == "required":
            missing_mandatory_fields.extend(err.message.split("'")[1::2])  # gets missing fields from the message
        validation_errors.append(
            {
                "path": list(err.path),
                "validator": err.validator,
                "message": err.message
            }
        )

    optional_fields = [
        key
        for key in schema.get("properties", {})
        if key not in metadata and key not in schema.get("required", [])
    ]

    result["valid"] = len(missing_mandatory_fields) == 0 and len(validation_errors) == 0

    if missing_mandatory_fields:
        result["missing_mandatory_fields"] = list(set(missing_mandatory_fields))

    result["missing_optional_fields"] = optional_fields

    if validation_errors:
        result["schema_validation_errors"] = validation_errors

    return result

def validate_notebooks(
    files: list,
    schema: str,
    # registry: Registry = None,
    abspath: bool = False
) -> list:
    return [
        validate_notebook(notebook, schema, #registry,
                       abspath=abspath) for notebook in files
    ]
