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
Usage: ./copy_add_ma.py [options]

options:
  -h        / --help               : このヘルプを表示

  -i <file> / --input-file <file>  : 入力ファイル名を設定 (省略時標準入力)
  -o <file> / --output-file <file> : 出力ファイル名を設定 (省略時標準出力)
  --input-encode <encode>          : 入力文字コードを設定 (省略時システム標準)
  --output-encode <encode>         : 出力文字コードを設定 (省略時システム標準)

  --header <num>                   : ヘッダ行数を設定 (省略時0)

  -l           / --lineno          : 行番号の出力を指定
  -f <data>    / --fix <data>      : 固定データの出力を指定
  -c <col-num> / --copy <col-num>  : そのまま出力する列を指定
  -s <col-num> / --sum <col-num>   : 累積和を出力する列を指定
  -a <col-num> <width> / --ma <col-num> <width> : 移動平均を出力する列を指定
  --smooth <col-num> <alpha>       : 急な変化を抑えたデータを出力する列を指定

ファイル名・文字コード・ヘッダ行数は、それぞれ0回か1回のみ設定可能。
出力指定(-f, -c, -s, -a)は何回でも指定でき、指定した順で出力される。
列の指定は一番左の列を1列目とする。
出力する行番号は1始まりで、ヘッダ行は含まない。

「急な変化を抑えたデータ」とは、0以上1以下の値alphaを用いて
「前回の出力値×(1-alpha) + 今回の入力値×alpha」で計算される値であり、
alphaが1に近いほど変化が早く反映される。
""".strip()

def toValue(inStr):
	ret = None
	try:
		ret = int(inStr)
	except ValueError:
		try:
			ret = float(inStr)
		except ValueError:
			pass
	return ret

import sys
import codecs
import csv

inputFileName = None
outputFileName = None
inputEncode = None
outputEncode = None
headerNum = None
outputs = []

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
				raise Exception("missing header count")
			i += 1
			headerNum = int(argv[i])
			if headerNum < 0:
				raise Exception("header count must be non-negative")
		elif argv[i] == '-l' or argv[i] == '--lineno':
			outputs.append(['l'])
		elif argv[i] == '-f' or argv[i] == '--fix':
			if i + 1 >= argc:
				raise Exception("missing data for fixed-data")
			i += 1
			outputs.append(['f', argv[i]])
		elif argv[i] == '-c' or argv[i] == '--copy':
			if i + 1 >= argc:
				raise Exception("missing column number for copy")
			i += 1
			col = int(argv[i])
			if col <= 0:
				raise Exception("column number must be positive")
			outputs.append(['c', col - 1])
		elif argv[i] == '-s' or argv[i] == '--sum':
			if i + 1 >= argc:
				raise Exception("missing column number for sum")
			i += 1
			col = int(argv[i])
			if col <= 0:
				raise Exception("column number must be positive")
			outputs.append(['s', col - 1])
		elif argv[i] == '-a' or argv[i] == '--ma':
			if i + 2 >= argc:
				raise Exception("missing column number or width for ma")
			i += 2
			col = int(argv[i - 1])
			width = int(argv[i])
			if col <= 0:
				raise Exception("column number must be positive")
			if width <= 0:
				raise Exception("ma width must be positive")
			outputs.append(['m', col - 1, width])
		elif argv[i] == '--smooth':
			if i + 2 >= argc:
				raise Exception("missing column number or alpha for ma")
			i += 2
			col = int(argv[i - 1])
			alpha = float(argv[i])
			if col <= 0:
				raise Exception("column number must be positive")
			if alpha < 0 or 1 < alpha:
				raise Exception("alpha must be between 0 and 1")
			outputs.append(['smooth', col - 1, alpha])
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
processBuffer = [[] if x[0] == 'm' else (None if x[0] == 'smooth' else 0) for x in outputs]
for row in csvReader:
	lineNo += 1
	outRow = []
	if headerNum is not None and lineNo <= headerNum:
		for o in outputs:
			if o[0] == 'l':
				outRow.append('lineno')
			elif o[0] == 'f':
				outRow.append(o[1])
			elif lineNo == 1 and o[0] == 's':
				outRow.append('sum of ' + row[o[1]])
			elif lineNo == 1 and o[0] == 'm':
				outRow.append('{0}-MA of {1}'.format(o[2], row[o[1]]))
			elif lineNo == 1 and o[0] == 'smooth':
				outRow.append('smoothed(alpha={0}) of {1}'.format(o[2], row[o[1]]))
			else:
				outRow.append(row[o[1]])
	else:
		for i in range(len(outputs)):
			o = outputs[i]
			if o[0] == 'l':
				outRow.append(lineNo if headerNum is None else (lineNo - headerNum))
			elif o[0] == 'f':
				outRow.append(o[1])
			elif o[0] == 's':
				v = toValue(row[o[1]])
				if v is None:
					outRow.append('')
				else:
					processBuffer[i] += v
					outRow.append(processBuffer[i])
			elif o[0] == 'm':
				v = toValue(row[o[1]])
				if v is None:
					outRow.append('')
				else:
					processBuffer[i].append(v)
					if len(processBuffer[i]) >= o[2]:
						processBuffer[i] = processBuffer[i][(len(processBuffer[i]) - o[2]):]
						sum = 0
						for pv in processBuffer[i]:
							sum += pv
						outRow.append(sum / o[2])
					else:
						outRow.append('')
			elif o[0] == 'smooth':
				v = toValue(row[o[1]])
				if v is None:
					outRow.append('')
				else:
					if processBuffer[i] is None:
						processBuffer[i] = v
					else:
						processBuffer[i] = processBuffer[i] * (1.0 - o[2]) + v * o[2]
					outRow.append(processBuffer[i])
			else:
				outRow.append(row[o[1]])
	csvWriter.writerow(outRow)

inputFile.close()
outputFile.close()
