#Data Validator

###Basic Info

This is a script meant to validate tables, specifically .csv files for now, according to a mix of table schema and custom constraints. The script is called in the form of "cli.py *.csv *.json" with optional attachment files being placed after.

The purpose of this collection of scripts it to provide a relatively simple and painless way to perform basic validation on any given csv file. While not a very powerful or robust toolset, the script has room for expansion, and at this point can quickly point out basic errors.

In terms of table schema, the format is near identical to that of https://frictionlessdata.io/specs/table-schema/. Please refer to there for the basics of schema.

A sample version of the simplified table schema used for this tool can be found in the samples folder. In addition, the file type and format of the attachment files can also be found. Attachment files should be named "column_name".json, with "column_name" being the field name meant to be attached to.

Currently, the errors are pushed to two files. The first, that is "file_name"_error_report.txt, is a json formatted structuring of the errors, with row, column, code, and messages in more human readable text shown. "file_name"_errorlog.csv is much of the more raw information, in easy to parse csv format.

The schema_generator script is a helper script meant to convert metadata into a table schema file-like object for use in the main validation tool.

###Running the Tool

####Step 1. Run the Script
- Run the script as follows, with the "sample" name being used as a placeholder for your name:
`python3 cli.py sample_table.csv sample_desc.json zip.json`
- In this case, the first two files are required, one being a csv, and the other being a json describing the csv. The third file is an optional file, allowing for further narrowing of valid information. It is named after the 'zip' field of the table.

####Step 2. The Output
- Once run, this produces two files, sampe_table_error_report.txt and sample_table_errorlog.csv. These have been described above.
