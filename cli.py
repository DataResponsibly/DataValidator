import sys

from valitool import vali

if len(sys.argv) > 2:
    print(sys.argv)
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
