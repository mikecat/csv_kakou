#coding: utf-8

"""
The MIT License (MIT)

Copyright (c) 2020 みけCAT

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

usage = """
Usage: ./reverse.py [options]

options:
  -h        / --help               : このヘルプを表示

  -i <file> / --input-file <file>  : 入力ファイル名を設定 (省略時標準入力)
  -o <file> / --output-file <file> : 出力ファイル名を設定 (省略時標準出力)
  --input-encode <encode>          : 入力文字コードを設定 (省略時システム標準)
  --output-encode <encode>         : 出力文字コードを設定 (省略時システム標準)

  --header <num>                   : ヘッダ行数を設定 (省略時0)

ファイル名・文字コード・ヘッダ行数は、それぞれ0回か1回のみ設定可能。
""".strip()

import sys
import codecs
import csv

inputFileName = None
outputFileName = None
inputEncode = None
outputEncode = None
headerNum = None

i = 1
argc = len(sys.argv)
argv = sys.argv
try:
	while i < argc:
		if argv[i] == '-h' or argv[i] == '--help':
			print(usage)
			sys.exit(0)
		elif argv[i] == '-i' or argv[i] == '--input-file':
			if inputFileName is not None:
				raise Exception("multiple -i or --input-file")
			if i + 1 >= argc:
				raise Exception("missing input file name")
			i += 1
			inputFileName = argv[i]
		elif argv[i] == '-o' or argv[i] == '--output-file':
			if outputFileName is not None:
				raise Exception("multiple -o or --output-file")
			if i + 1 >= argc:
				raise Exception("missing output file name")
			i += 1
			outputFileName = argv[i]
		elif argv[i] == '--input-encode':
			if inputEncode is not None:
				raise Exception("multiple --input-encode")
			if i + 1 >= argc:
				raise Exception("missing input encoding")
			i += 1
			inputEncode = argv[i]
		elif argv[i] == '--output-encode':
			if outputEncode is not None:
				raise Exception("multiple --output-encode")
			if i + 1 >= argc:
				raise Exception("missing output encoding")
			i += 1
			outputEncode = argv[i]
		elif argv[i] == '--header':
			if headerNum is not None:
				raise Exception("multiple --header")
			if i + 1 >= argc:
				raise Exception("missing header count missing")
			i += 1
			headerNum = int(argv[i])
			if headerNum < 0:
				raise Exception("header count must be non-negative")
		else:
			raise Exception("unknown option " + argv[i])
		i += 1
except Exception as e:
	sys.stderr.write('error: ' + str(e) + '\n')
	sys.exit(1)

inputFile = open(inputFileName, 'r', newline='') if inputFileName is not None else sys.stdin
outputFile = open(outputFileName, 'w', newline='') if outputFileName is not None else sys.stdout
if outputFileName is None:
	sys.stdout.reconfigure(newline='')

inputFileReader = codecs.getreader(inputEncode)(inputFile) if inputEncode is not None else inputFile
outputFileWriter = codecs.getwriter(outputEncode)(outputFile) if outputEncode is not None else outputFile

csvReader = csv.reader(inputFileReader)
csvWriter = csv.writer(outputFileWriter)

lineNo = 0
bufferedRows = []
for row in csvReader:
	lineNo += 1
	if headerNum is not None and lineNo <= headerNum:
		csvWriter.writerow(row)
	else:
		bufferedRows.append(row)

bufferSize = len(bufferedRows)
for i in range(bufferSize):
	csvWriter.writerow(bufferedRows[bufferSize - 1 - i])
