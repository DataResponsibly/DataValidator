import sys

from valitool import vali

'''
This is the cli for the validation tool. This is the script to run to utilize the tool.
The other scripts are kept modular.
'''

if len(sys.argv) > 2:
    csv_file = sys.argv[1]
    desc_file = sys.argv[2]
    attachments = []
    if len(sys.argv) > 3:
        for i in range(3,len(sys.argv)):
            print(i)
            attachments.append(sys.argv[i])
    vali(csv_file, desc_file, attachments)
else:
    print("Insufficient data. Please attach at the least a csv and a description file (format in readme).")
