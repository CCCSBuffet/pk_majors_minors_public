import csv
import sys
import os
from getopt import getopt, GetoptError

Major = ''
Minor = ''
Folder = '.'
DoGenderData = False
DoChurnByTerm = False
DoChurnByStudent = False
EventData = { }

def PrintHelp():
	print('Usage:')
	print('-c	--churn_by_month	output churn data by month')
	print('-C	--churn_by_student	output churn data by student')
	print('-f	--folder		arg is the folder (default is current directory)')
	print('-g	--gender		output gender data')
	print('-h	--help			print this text and exit')
	print('-m	--minor			arg is the Minor text (remember double quotes if text contains spaces)')
	print('-M	--major			arg is the Major text (remember double quotes if text contains spaces)')

def HandleCommandLine():
	global Major, Minor, Folder
	global DoGenderData, DoChurnByTerm, DoChurnByStudent
	short_opts = 'cCf:ghM:m:'
	long_opts = ['help', 'major=', 'minor=', 'folder=', 'churn_by_month', 'churn_by_student', 'gender']
	try:
		opts, a = getopt(sys.argv[1:], short_opts, long_opts)
	except GetoptError as ex:
		print(ex)
		PrintHelp()
		exit(1)
	for o, a in opts:
		if o in ('-f', '--folder'):
			Folder = a
		elif o in ('-h', '--help'):
			PrintHelp()
			exit(0)
		elif o in ('-m', '--minor'):
			Minor = a
			raise NotImplementedError('Assumes minor matches major')
		elif o in ('-M', '--major'):
			Major = a
			Minor = a
		elif o in ('-g', '--gender'):
			DoGenderData = True
		elif o in ('-c', '--churn_by_month'):
			DoChurnByTerm = True
		elif o in ('-g', '--churn_by_student'):
			DoChurnByStudent = True
	Major = Major.lstrip()
	if Major == '':
		print('-M or --major required')
		exit(1)
	return

def EnumerateFolder(folder):
	files = []
	if not os.path.isdir(folder):
		exit(folder + ' is not a directory or cannot be found')
	for root, _, f in os.walk(folder):
		for file in f:
			if file.endswith("csv"):
				full_name = os.path.join(root, file)
				files.append(full_name)
	files.sort()
	return files

def	GetType(line):
	if Major in [line['Major 1 Description'], line['Major 2 Description']]:
		return 'majors'
	elif Minor in [line['Minor 1 Description'], line['Minor 2 Description'], line['Minor 3 Description']]:
		return 'minors'
	return None

def GetGender(line):
	if line['Gender Code'] == 'F':
		return 0
	else:
		return 1

def ReadAllData(files):
	all_data = [ ]
	for file in files:
		with open(file) as fin:
			report = { }
			base = os.path.basename(file)[3:-4]
			report['name'] = base
			report['year'] = base[0:4]
			report['month'] = base[-2:]
			for type in ['majors', 'minors']:
				report[type] = { }
				report[type]['gender'] = [ 0, 0 ]
				report[type]['student'] = { }
			reader = csv.DictReader(fin)
			for line in reader:
				type = GetType(line)
				g = line['Gender Code']
				email = line['Carthage E-mail']
				gpa = line['Cumulative GPA']
				if type == None:
					continue
				if file == files[0]:
					EventData[email] = [ g, { type: 'Add', 'when': base, 'gpa': gpa} ]
				report[type]['gender'][GetGender(line)] += 1
				report[type]['student'][email] = line
			all_data.append(report)
	return all_data

def ExtractGender(d):
	f = d['gender'][0]
	m = d['gender'][1]
	r = 0
	if m > 0:
		r = f / (f + m)
	return f, m, r 

def MakeGenderPlot(data):
	print('{:<10s}'.format('Report'), end='')
	print('{:<25s} '.format('Majors'), end='')
	print('{:<18s}'.format('Minors'), end='')
	print()
	print('{:<10s}'.format(''), end='')
	print('{:>5s}{:>5s}{:>6s}{:>8s} '.format('F', 'M', 'Total', 'Ratio'), end='')
	print('{:>5s}{:>5s}{:>6s}{:>8s}'.format('F', 'M', 'Total', 'Ratio'), end='')
	print()
	for report in data:
		print('{:<10s}'.format(report['name']), end='')
		f, m, r = ExtractGender(report['majors'])
		print('{:>5d}{:>5d}{:>6d}{:>8.2f} '.format(f, m, f + m, r), end='')
		f, m, r = ExtractGender(report['minors'])
		print('{:>5d}{:>5d}{:>6d}{:>8.2f}'.format(f, m, f + m, r), end='')
		print()

def GetDelta(type, r1, r2):
	global EventData
	s1 = set(r1[type]['student'].keys())
	s2 = set(r2[type]['student'].keys())
	differences = [ s2.difference(s1), s1.difference(s2) ]
	counter = 0
	for s in differences:
		r =  { }
		direction = ''
		if counter == 0:
			r = r2
			direction = 'Add'
			print('Adds  - In', r2['name'], 'but not in', r1['name'])
		else:
			r = r1
			direction = 'Drop'
			print('Drops - In', r1['name'], 'but not in', r2['name'])
		something_printed = False
		for email in s:
			l = r[type]['student'][email]
			g = l['Gender Code']
			gpa = float(l['Cumulative GPA'])
			pgy = l['Planned Graduation Year']
			pgs = l['Planned Graduation Session Code']

			if email not in EventData.keys():
				EventData[email] = [ g, { type: direction, 'when': r['name'], 'gpa': gpa, 'pgy': pgy, 'pgs': pgs } ]
			else:
				EventData[email].append([ { type: direction, 'when': r['name'], 'gpa': gpa, 'pgy': pgy, 'pgs': pgs } ])
			print('{:<12s} {:<12s} {:<1s}'.format(l['Last Name'], l['First Name'], g), end='')
			print(' {:<4.3f}'.format(gpa), end='')
			print(' {:<26s}'.format(email), end='')
			print(' {:<6s}'.format(pgy), end='')
			print(' {:<6s}'.format(pgs), end='')
			print()
			something_printed = True
		if something_printed == False:
			print('None')
		if counter == 0:
			print()
		counter += 1

if __name__ == "__main__":
	HandleCommandLine()
	files = EnumerateFolder(Folder)
	if len(files) == 0:
		exit('No CSV files found')
	data = ReadAllData(files)
	if DoGenderData:
		MakeGenderPlot(data)
	if DoChurnByTerm:
		print('--- MAJORS ---')
		print()
		for index in range(len(data) - 1):
			GetDelta('majors', data[index], data[index + 1])
			print()	
		print()
		print('--- MINORS ---')
		print()
		for index in range(len(data) - 1):
			GetDelta('minors', data[index], data[index + 1])
			print()
	#print(EventData)