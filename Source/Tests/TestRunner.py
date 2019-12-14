import subprocess
import os
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--files', type=str, help='Comma separated test filenames')
args = parser.parse_args()

test_files = {x for x in os.listdir() if re.search(r'.*_test.py', x)}

if args.files:
	arg_files = set(args.files.split(','))
	test_files = test_files.intersection(arg_files)

	if test_files != arg_files:
		print('Invalid Files:', ', '.join(arg_files-test_files))
		parser.print_help()
	else:
		for test in test_files:
			subprocess.Popen(f'pytest {test}', subprocess.STARTF_USESTDHANDLES | subprocess.STARTF_USESHOWWINDOW).communicate()

else:
	subprocess.Popen(f'pytest', subprocess.STARTF_USESTDHANDLES | subprocess.STARTF_USESHOWWINDOW).communicate()
