import json
import csv
import sys
import os

import pandas as pd
import numpy as np

'''
For file attachments, the file should be a .json with the name <column>.json, in the format:
{
    <column>: [<parameters>]
}

This script takes in a piece of metadata from the DataResponsibly Data Synthesizer
and creates a Table Schema of the provided dataset, as detailed at https://frictionlessdata.io/specs/table-schema/
'''

def schema_gen(file,attachments,path):

    if len(attachments) > 0: # Used to attach files in the format described above.
        has_file = True
    else:
        has_file = False
    print(has_file)
    print(path)
    if path != "":
        path = path + '/'
    schema = { 'primaryKey': '', 'fields' : [] }
    field_template = { 'name': '', 'type': '' } # template used to base field data off of
    field_list = []
    with open(file) as fp:
        y = fp.read()
        desc_json = json.loads(y)
        keys = desc_json['attribute_description'].keys()
        for key in keys:
            is_ss = False
            field = { 'name': '', 'type': '' }
            field['name'] = key
            type = desc_json['attribute_description'][key]['data_type'].lower()
            if type == 'socialsecuritynumber': # TODO: Add in constraint for SSN
                field['type'] = 'string'
                is_ss = True
            else:
                field['type'] = type
            if has_file:
                filename = key + '.json'
                if path + key +'.json' in attachments: # If a file is attached, creates enumerated list constraint for validation
                    with open('samples/' + key +'.json') as sp:
                        json_raw = sp.read()
                        enums = json.loads(json_raw)
                        field['constraints'] = {}
                        field['constraints']['enum'] = enums[key]

            if desc_json['attribute_description'][key]['required']:
                if 'constraints' not in field.keys():
                    field['constraints'] = {}
                field['constraints']['required'] = True
            if desc_json['attribute_description'][key]['unique']:
                if 'constraints' not in field.keys():
                    field['constraints'] = {}
                field['constraints']['unique'] = True


            field_list.append(field)
        schema['fields'] = field_list
    return schema