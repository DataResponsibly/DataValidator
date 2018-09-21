import json
import csv
import sys
import io
import os
import ast
import smtplib

from goodtables import validate,check,Error,config
from goodtables import Inspector
import pandas

from schema_generator import schema_gen
"""
Example of goodtables report.

{
    "time": 0.025,
    "valid": false,
    "error-count": 7,
    "table-count": 1,
    "tables": [
        {
            "datapackage": "{'name': 'sample_table', 'title': 'sample_table', 'resources': [{'name': 'sample_table', 'path': 'samples/sample_table.csv', 'schema': {'primaryKey': '', 'fields': [{'name': 'key', 'type': 'integer', 'constraints': {'unique': True}}, {'name': 'zip', 'type': 'string'}, {'name': 'tract', 'type': 'integer'}, {'name': 'latitude', 'type': 'number'}, {'name': 'longitude', 'type': 'number'}, {'name': 'soc', 'type': 'string', 'constraints': {'unique': True, 'pattern': '[0-9]{3}-?[0-9]{2}-?[0-9]{4}'}}]}}]}",
            "time": 0.011,
            "valid": false,
            "error-count": 7,
            "row-count": 6,
            "source": "./samples/sample_table.csv",
            "headers": [
                "key",
                "zip",
                "tract",
                "latitude",
                "longitude",
                "soc"
            ],
            "format": "inline",
            "schema": "table-schema",
            "errors": [
                {
                    "code": "pattern-constraint",
                    "row-number": 2,
                    "column-number": 6,
                    "message": "The value \"132-123-1441\" in row 2 and column 6 does not conform to the pattern constraint of \"[0-9]{3}-?[0-9]{2}-?[0-9]{4}\""
                },
                {
                    "code": "pattern-constraint",
                    "row-number": 3,
                    "column-number": 6,
                    "message": "The value \"123-143-1341\" in row 3 and column 6 does not conform to the pattern constraint of \"[0-9]{3}-?[0-9]{2}-?[0-9]{4}\""
                },
                {
                    "code": "unique-constraint",
                    "row-number": 4,
                    "column-number": 1,
                    "message": "Rows 2, 3, 4 has unique constraint violation in column 1"
                },
                {
                    "code": "pattern-constraint",
                    "row-number": 4,
                    "column-number": 6,
                    "message": "The value \"13413441513\" in row 4 and column 6 does not conform to the pattern constraint of \"[0-9]{3}-?[0-9]{2}-?[0-9]{4}\""
                },
                {
                    "code": "type-or-format-error",
                    "row-number": 5,
                    "column-number": 3,
                    "message": "The value \"twelve\" in row 5 and column 3 is not type \"integer\" and format \"default\""
                },
                {
                    "code": "pattern-constraint",
                    "row-number": 5,
                    "column-number": 6,
                    "message": "The value \"124-134-4144\" in row 5 and column 6 does not conform to the pattern constraint of \"[0-9]{3}-?[0-9]{2}-?[0-9]{4}\""
                },
                {
                    "code": "pattern-constraint",
                    "row-number": 6,
                    "column-number": 6,
                    "message": "The value \"4433443\" in row 6 and column 6 does not conform to the pattern constraint of \"[0-9]{3}-?[0-9]{2}-?[0-9]{4}\""
                }
            ]
        }
    ],
    "warnings": [],
    "preset": "datapackage"
}

"""
def validation(datapackage,cust,path_and_filename,path):
    """
    datapackage: dataset uploaded in datapackage
        A datapackage is a json like data structure, that contains the original
        dataset, as well as the schema that was generated previously, e.g.,
        {
            "name": filename,
            "title": filename,
            "resources": [
                    {
                        "name": filename,
                        "path": path_and_filename,
                        "schema": schema
                    }
                ]
        }

    cust: eventual housing for custom error messages, NYI
    path_and_filename: name of the file Uploaded
    path: directory of the file
    """
    inspector = Inspector()
    inspector.__init__(row_limit=100000,error_limit=100000) # arbitrary row limit
    report = inspector.inspect(datapackage)
    print(json.dumps(report,indent=4))
    pretty_str = ''
    if path != "":
        path = path + '/'

    if not report['valid']: # an error report will only be sent if there are issues to be found
        for table in report['tables']:
            s = ast.literal_eval(table['datapackage'])
            filename = s['name'] + "_error_dump.txt"
            with open(path + filename,'w',) as fp:
                error_rows = []
                for error in table['errors']:
                    row = error['row-number']
                    error_rows.append(row)

                    if 'col' in error.keys():
                        col = error['column-number']
                    else:
                        col = ""
                    err_str = error['message']
                    code = ""
                    for err in cust:
                        # This replaces certain error codes with better formatted, more human readable variants.
                        if col in err['columns'] and error['code'] != 'required-constraint' and error['code'] != 'type-or-format-error':
                            err_str = err_str[:err_str.find("\"",err_str.find("\"")+1,)+1]
                            value = err_str[err_str.find("\"")+1:]
                            value = value[:len(value)-1]
                            newrow = row - 1
                            err_str = err_str + " in row " + str(newrow) + " and column " + str(col) + err['message']
                            code = err['name']
                            #print(code)
                            break; # multiple codes are possible, but the custom code should be given advantage non-constraints or type errors.
                        elif error['code'] == 'required-constraint':
                            value = ''
                            code = error['code']
                        else:
                            new_err_str = err_str[:err_str.find("\"",err_str.find("\"")+1,)+1]
                            value = new_err_str[new_err_str.find("\"")+1:]
                            value = value[:len(value)-1]
                            code = error['code']
                            pretty_str = pretty_str + err_str + "\n"
                            '''
                with open(path + path_and_filename + '_errorlog.csv','w') as sp:
                    with open(path + path_and_filename + '.csv','r') as rp:
                        csv_r = csv.reader(rp)
                        csv_w = csv.writer(sp)
                        headers = csv_r.__next__()
                        csv_w.writerow(headers)
                        row_number = 2
                        for row in csv_r:
                            if row_number in error_rows:
                                csv_w.writerow(row)
                            row_number = row_number + 1
                            '''
            with open(path + path_and_filename + '_error_report.json','w') as fp:
                fp.write(json.dumps(table['errors'],indent=4))
            return table['errors']
    else:
        return "All clear"


def vali(path_and_filename,desc_file,attachments):
    filename, file_extension = os.path.splitext(path_and_filename)
    assert file_extension == '.csv', 'Please use csv file.'
    f_path = filename.split('/')
    filename = f_path[len(f_path)-1]
    del f_path[len(f_path)-1]
    path = '/'.join(f_path)
    schema = schema_gen(desc_file,[],path) # TODO: Enhance combatibility
    print(json.dumps(schema, indent=4))
    #custom_error = [{'name': 'ssn', 'columns': [], 'message': ' is not a correctly formatted Social Security Number.'},{'name': 'phil_tract', 'columns': [], 'message': ' is not a Philadelphia Census Tract.'},{'name': 'lat', 'columns': [], 'message': ' is not a latitude near Philadelphia.'},{'name': 'lon', 'columns': [], 'message': ' is not a longitude near Philadelphia.'}]
    # The above is an example of custom error formatting.
    # col_count = 1
    # col_count = col_count + 1
    custom_error = []
    data_package_json = { "name": filename, "title": filename, "resources": [{"name": filename, "path": path_and_filename, "schema": schema}]}
    print(data_package_json)
    # The csv and schema must be loaded together into a datapackage for use with goodtables
    if file_extension == '.csv':
        return validation(data_package_json,custom_error,filename,path)
