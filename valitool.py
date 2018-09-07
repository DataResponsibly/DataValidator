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

def validation(csv_,cust,file_name):
    inspector = Inspector()
    inspector.__init__(row_limit=100000,error_limit=100000) # arbitrary row limit
    report = inspector.inspect(csv_)
    email_data = []
    pretty_str = ''

    if not report['valid']: # an error report will only be sent if there are issues to be found
        for table in report['tables']:
            s = ast.literal_eval(table['datapackage'])
            filename = s['name'] + "_error_dump.txt"
            print(table)
            with open(filename,'w',) as fp:
                error_rows = []
                for error in table['errors']:
                    print(error)
                    row = error['row-number']
                    error_rows.append(row)
                    if 'col' in error.keys():
                        col = error['column-number']
                    else:
                        col = ""
                    err_str = error['message']
                    code = ""
                    for err in cust:
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
                    email_data.append({'code': code, 'row': row, 'col': col, 'value': value})
                with open(file_name + '_errorlog.csv','w') as sp:
                    with open('samples/' + file_name + '.csv','r') as rp:
                        csv_r = csv.reader(rp)
                        csv_w = csv.writer(sp)
                        headers = csv_r.__next__()
                        csv_w.writerow(headers)
                        row_number = 2
                        for row in csv_r:
                            if row_number in error_rows:
                                csv_w.writerow(row)
                            row_number = row_number + 1


            #return notification('',email_data,pretty_str,s['name'])
            return table['errors']
    else:
        return "All clear"
def vali(file_name,desc_file,attachments):
    filename, file_extension = os.path.splitext(file_name)
    print(filename)
    f_path = filename.split('/')
    print(f_path)
    filename = f_path[len(f_path)-1]
    del f_path[len(f_path)-1]
    path = '/'.join(f_path)
    schema = schema_gen(desc_file,attachments,path) # TODO: Enhance combatibility
    custom_error = [{'name': 'phil_zip', 'columns': [], 'message': ' is not a Philadelphia zip code.'},{'name': 'phil_tract', 'columns': [], 'message': ' is not a Philadelphia Census Tract.'},{'name': 'lat', 'columns': [], 'message': ' is not a latitude near Philadelphia.'},{'name': 'lon', 'columns': [], 'message': ' is not a longitude near Philadelphia.'}]
    col_count = 1
    for field in schema['fields']:
        if 'constraints' in field:
            if 'custom' in field['constraints']:
                custom = field['constraints']['custom']
                if custom == 'lat': # lat refers to any latitude that -could- be in and around Philadelphia
                    del field['constraints']['custom']
                    field['constraints']['minimum'] = 38
                    field['constraints']['maximum'] = 42
                    custom_error[2]['columns'].append(col_count)
                elif custom == 'lon': # lon refers to any longitude that -could- be in and around Philadelphia
                    del field['constraints']['custom']
                    field['constraints']['maximum'] = -73
                    field['constraints']['minimum'] = -77
                    custom_error[3]['columns'].append(col_count)
        col_count = col_count + 1

    data_package_json = { "name": filename, "title": filename, "resources": [{"name": filename, "path": file_name, "schema": schema}]}
    # The csv and schema must be loaded together into a datapackage for use with goodtables
    if file_extension == '.csv':
        #anamoly_detection(file_name)
        return validation(data_package_json,custom_error,filename)
