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
Usage: ./candle.py [options]

options:
  -h        / --help                : このヘルプを表示

  -i <file> / --input-file <file>  : 入力ファイル名を設定 (省略時標準入力)
  -o <file> / --output-file <file> : 出力ファイル名を設定 (省略時標準出力)
  --input-encode <encode>          : 入力文字コードを設定 (省略時システム標準)
  --output-encode <encode>         : 出力文字コードを設定 (省略時システム標準)

  --header <num>                   : ヘッダ行数を設定 (省略時0)

  -t <col-num> / --time <col-num>  : 時刻が格納された行を指定 (省略時1)
  -v <col-num> / --value <col-num> : 値が格納された行を指定 (省略時2)

  -s <value> / --span <value>      : 計算を行う間隔を指定 (省略時day)
    value: month / week / day / (整数)h / (整数)m / (整数)s
  --week-start <value>             : 週足の開始日を指定 (省略時sun)
    value: sun / mon / tue / wed / thu / fri / sat

  --input-date <format> : 入力の日時形式を指定 (省略時 %Y/%m/%d %H:%M:%S )
  --output-date <format> : 出力の日時形式を指定
    (省略時、間隔が month / week / day のとき %Y/%m/%d )
    (省略時、間隔が それ以外           のとき %Y/%m/%d %H:%M:%S )

各オプションは、それぞれ0回か1回のみ設定可能。
列の指定は一番左の列を1列目とする。
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
import datetime

inputFileName = None
outputFileName = None
inputEncode = None
outputEncode = None
headerNum = None
timeCol = None
valueCol = None
span = None
weekStart = None
inputDate = None
outputDate = None

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
		elif argv[i] == '-t' or argv[i] == '--time':
			if timeCol is not None:
				raise Exception("multiple -t or --time")
			if i + 1 >= argc:
				raise Exception("missing time column")
			i += 1
			timeCol = int(argv[i])
			if timeCol <= 0:
				raise Exception("time column must be positive")
		elif argv[i] == '-v' or argv[i] == '--value':
			if valueCol is not None:
				raise Exception("multiple -v or --value")
			if i + 1 >= argc:
				raise Exception("missing value column")
			i += 1
			valueCol = int(argv[i])
			if valueCol <= 0:
				raise Exception("value column must be positive")
		elif argv[i] == '-s' or argv[i] == '--span':
			if span is not None:
				raise Exception("multiple -s or --span")
			if i + 1 >= argc:
				raise Exception("missing span")
			i += 1
			span = argv[i]
		elif argv[i] == '--week-start':
			if weekStart is not None:
				raise Exception("multiple --week-start")
			if i + 1 >= argc:
				raise Exception("missing week start")
			i += 1
			weekStart = argv[i]
		elif argv[i] == '--input-date':
			if inputDate is not None:
				raise Exception("multiple --input-date")
			if i + 1 >= argc:
				raise Exception("missing input date format")
			i += 1
			inputDate = argv[i]
		elif argv[i] == '--output-date':
			if outputDate is not None:
				raise Exception("multiple --output-date")
			if i + 1 >= argc:
				raise Exception("missing output date format")
			i += 1
			outputDate = argv[i]
		else:
			raise Exception("unknown option " + argv[i])
		i += 1
except Exception as e:
	sys.stderr.write('error: ' + str(e) + '\n')
	sys.exit(1)

if headerNum is None: headerNum = 0
if timeCol is None: timeCol = 1
if valueCol is None: valueCol = 2
if span is None : span = "day"
if weekStart is None : weekStart = "sun"
if inputDate is None : inputDate = "%Y/%m/%d %H:%M:%S"
if outputDate is None : outputDate = "%Y/%m/%d" if span in ["month", "week", "day"] else "%Y/%m/%d %H:%M:%S"

weekStartNo = None
weekNames = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
for i in range(len(weekNames)):
	if weekStart == weekNames[i]:
		weekStartNo = i

intervalSeconds = None

def getMonthKey(date):
	return datetime.datetime(date.year, date.month, 1)

def getWeekKey(date):
	day = datetime.datetime(date.year, date.month, date.day)
	delta = (day.weekday() - weekStartNo + 7) % 7
	return day - datetime.timedelta(days=delta)

def getDayKey(date):
	return datetime.datetime(date.year, date.month, date.day)

def getSecondKey(date):
	day = datetime.datetime(date.year, date.month, date.day)
	delta = date - day
	seconds = (delta.seconds // intervalSeconds) * intervalSeconds
	return day + datetime.timedelta(seconds=seconds)

getKey = None

if span == "month":
	getKey = getMonthKey
elif span == "week":
	if weekStartNo is None:
		sys.stderr.write("error: invalid week start\n")
		sys.exit(1)
	getKey = getWeekKey
elif span == "day":
	getKey = getDayKey
elif span[-1] in ["h", "m", "s"]:
	try:
		intervalSeconds = int(span[:-1])
	except ValueError:
		sys.stderr.write("error: invalid span\n")
		sys.exit(1)
	if intervalSeconds <= 0:
		sys.stderr.write("error: span must be positive\n")
		sys.exit(1)
	if span[-1] == "h":
		intervalSeconds *= 60 * 60
	elif span[-1] == "m":
		intervalSeconds * 60
	if (24 * 60 * 60) % intervalSeconds != 0:
		sys.stderr.write("error: no remainder allowed for sub-day span\n")
		sys.exit(1)
	getKey = getSecondKey

inputFile = open(inputFileName, 'r', newline='') if inputFileName is not None else sys.stdin
outputFile = open(outputFileName, 'w', newline='') if outputFileName is not None else sys.stdout
if outputFileName is None:
	sys.stdout.reconfigure(newline='')

inputFileReader = codecs.getreader(inputEncode)(inputFile) if inputEncode is not None else inputFile
outputFileWriter = codecs.getwriter(outputEncode)(outputFile) if outputEncode is not None else outputFile

csvReader = csv.reader(inputFileReader)
csvWriter = csv.writer(outputFileWriter)

prevKey = None

beginning = None
high = None
low = None
prevValue = None

csvWriter.writerow(["date", "open", "high", "low", "close"])

lineNo = 0
for row in csvReader:
	lineNo += 1
	if lineNo <= headerNum:
		continue
	key = getKey(datetime.datetime.strptime(row[timeCol - 1], inputDate))
	value = toValue(row[valueCol - 1])
	if prevKey is None or prevKey < key:
		if prevKey is not None:
			csvWriter.writerow([prevKey.strftime(outputDate), beginning, high, low, prevValue])
		prevKey = key
		beginning = value
		high = value
		low = value
	elif prevKey == key:
		if value > high: high = value
		if value < low: low = value
	else:
		sys.stderr.write("error: date must be ascending order")
		sys.exit(1)
	prevValue = value

if prevKey is not None:
	csvWriter.writerow([key.strftime(outputDate), beginning, high, low, prevValue])

inputFile.close()
outputFile.close()
