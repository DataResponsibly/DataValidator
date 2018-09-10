#Data Validator

This is a script meant to validate tables, specifically .csv files for now, according to a mix of table schema and custom constraints. The script is called in the form of "cli.py *.csv *.json" with optional attachment files being placed after.

The purpose of this collection of scripts it to provide a relatively simple and painless way to perform basic validation on any given csv file. While not a very powerful or robust toolset, the script has room for expansion, and at this point can quickly point out basic errors.

In terms of table schema, the format is near identical to that of https://frictionlessdata.io/specs/table-schema/. Please refer to there for the basics of schema.

A sample version of the simplified table schema used for this tool can be found in the samples folder. In addition, the file type and format of the attachment files can also be found. Attachment files should be named "column_name".json, with "column_name" being the field name meant to be attached to.

Currently, the errors are pushed to a text file, bearing the name of the original csv, plus "_error_dump", and additional printed to console. In addition to all of this, a

The schema_generator script is a helper script meant to convert metadata into a table schema file-like object for use in the main validation tool.


*Currently, the unique and required modifiers have low compatibility with one another, and a fix is being worked on.*
