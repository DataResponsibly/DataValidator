import json
import csv
import sys
import os

import pandas as pd
import numpy as np

"""
An example of schema output:

{
    "primaryKey": "",
    "fields": [
        {
            "name": "key",
            "type": "integer",
            "constraints": {
                "unique": true
            }
        },
        {
            "name": "zip",
            "type": "string"
        },
        {
            "name": "tract",
            "type": "integer"
        },
        {
            "name": "latitude",
            "type": "number"
        },
        {
            "name": "longitude",
            "type": "number"
        },
        {
            "name": "soc",
            "type": "string",
            "constraints": {
                "unique": true,
                "pattern": "[0-9]{3}-?[0-9]{2}-?[0-9]{4}"
            }
        }
    ]
}
"""

def schema_gen(input_file,attachments,path):
    '''
    This script takes in a simplified schema provided by the user, and changes it into a schema
    that is recognizable by the goodtables library, which is defined at https://frictionlessdata.io/specs/table-schema/

    input_file: the json description/schema file
    attachments: a list of file names.
        For file attachments, the file should be a .json with the name <column>.json, in the format:
        {
            <column>: [<parameters>]
        }
    path: directory of the input_file

    '''

    if len(attachments) > 0: # Used to attach files in the format described above.
        has_customized_domains = True
    else:
        has_customized_domains = False
    if path != "":
        path = path + '/'
    schema = { 'primaryKey': '', 'fields' : [] }
    field_template = { 'name': '', 'type': '' } # template used to base field data off of
    field_list = []
    with open(input_file) as fp:
        y = fp.read()
        desc_json = json.loads(y)
        keys = desc_json['attribute_description'].keys()
        for key in keys:
            is_ssn = False
            field = { 'name': '', 'type': '' }
            field['name'] = key
            type = desc_json['attribute_description'][key]['data_type'].lower()
            if type == 'float':
                type = 'number'
            elif type == 'socialsecuritynumber':
                type = 'string'
                is_ssn = True


            field['type'] = type
            if has_customized_domains:
                filename = key + '.json'
                if path + key + '.json' in attachments: # If a file is attached, creates enumerated list constraint for validation
                    with open(path + key +'.json') as sp:
                        json_raw = sp.read()
                        enums = json.loads(json_raw)
                        if 'constraints' not in field.keys():
                            field['constraints'] = {}
                        field['constraints']['enum'] = enums[key]
            if 'required' in desc_json['attribute_description'][key].keys() and 'unique' not in desc_json['attribute_description'][key].keys(): # Check for required constraint.
                if desc_json['attribute_description'][key]['required']:
                    if 'constraints' not in field.keys():
                        field['constraints'] = {}
                    field['constraints']['required'] = True
            if 'unique' in desc_json['attribute_description'][key].keys(): # Check for unique constraint.
                if desc_json['attribute_description'][key]['unique']:
                    if 'constraints' not in field.keys():
                        field['constraints'] = {}
                    field['constraints']['unique'] = True
            '''
            The pattern matching constraint of goodtables, even on the current
            version, is slightly bugged. Due to a false error call, any calls
            to the pattern matching constraint will immediately crash the program.

            The fix is rather simple, where on the path denoted by goodtables/checks,
            find the file pattern_constraint.py. Once found, go to line 19 and change
            'cells.remove(error.cell)' to 'cells.remove(error._cell)'. While this seems
            simple, the official github has yet to push this, or any other fix through.

            More info can be found at: https://github.com/frictionlessdata/goodtables-py/issues/264
            '''
            if is_ssn:
                if 'constraints' not in field.keys():
                    field['constraints'] = {}
                field['constraints']['pattern'] = '[0-9]{3}-?[0-9]{2}-?[0-9]{4}'

            schema['fields'].append(field)
        # schema['fields'] = field_list
    return schema
