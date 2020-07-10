import csv
import sys
import os
from getopt import getopt, GetoptError

Major_Literal = 'Major'
Minor_Literal = 'Minor'
Major = ''
Minor = ''
Folder = '.'
DoGenderData = False
DoChurnByMonth = False
DoChurnByStudent = False
DoExpectedGraduation = False
DoMinorEmail = False
DoMajorEmail = False
DoPairing = False

EventData = { }
ExpGradData = { }
CurrentEmailAddresses = { }

def PrintHelp():
	print('Usage:')
	print('-c	--churn_by_month	output churn data by month')
	print('-C	--churn_by_student	output churn data by student')
	print('-e	--expected_grad		expected graduation year')
	print('-f	--folder		arg is the folder (default is current directory)')
	print('-g	--gender		output gender data')
	print('-h	--help			print this text and exit')
	print('-l	--list_minors		output email addresses of current minors')
	print('-L	--list_majors		output email addresses of current majors')
	print('-m	--minor			arg is the Minor text (remember double quotes if text contains spaces)')
	print('-M	--major			arg is the Major text (remember double quotes if text contains spaces)')
	print('-p	--pairings		calculates distributions of Major and Minor pairings')

def HandleCommandLine():
	global Major, Minor, Folder
	global DoGenderData, DoChurnByMonth, DoChurnByStudent
	global DoExpectedGraduation, DoMajorEmail, DoMinorEmail
	global DoPairing

	short_opts = 'cCef:ghlLM:m:p'
	long_opts = ['pairings', 'help', 'major=', 'minor=', 'folder=', 'churn_by_month', 'churn_by_student', 'gender', 'expected_grad', 'list_minors', 'list_majors']
	try:
		opts, a = getopt(sys.argv[1:], short_opts, long_opts)
	except GetoptError as ex:
		print(ex)
		PrintHelp()
		exit(1)
	for o, a in opts:
		if o in ('-p', '--pairings'):
			DoPairing = True
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
			DoChurnByMonth = True
		elif o in ('-C', '--churn_by_student'):
			DoChurnByStudent = True
		elif o in ('-e', '--expected_grad'):
			DoExpectedGraduation = True
		elif o in ('-l', '--list_minors'):
			DoMinorEmail = True
		elif o in ('-L', '--list_majors'):
			DoMajorEmail = True
			
	Major = Major.lstrip()
	if Major == '':
		print('-M or --major required')
		exit(1)
	if DoChurnByMonth and DoChurnByStudent:
		print('Cannot produce both churn reports in one instance of the program.')
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
		return Major_Literal
	elif Minor in [line['Minor 1 Description'], line['Minor 2 Description'], line['Minor 3 Description']]:
		return Minor_Literal
	return None

def GetGender(line):
	if line['Gender Code'] == 'F':
		return 0
	else:
		return 1

def ReadAllData(files):
	global ExpGradData, CurrentEmailAddresses
	global Pairings
	Pairings = { }
	all_data = [ ]
	literals = [ Major_Literal, Minor_Literal ]
	for l in literals:
		ExpGradData[l] = { }
		CurrentEmailAddresses[l] = [ ]
		Pairings[l] = { }

	for file in files:
		with open(file) as fin:
			report = { }
			
			base = os.path.basename(file)[3:-4]
			report['name'] = base
			report['year'] = base[0:4]
			report['month'] = base[-2:]

			for type in [Major_Literal, Minor_Literal]:
				report[type] = { }
				report[type]['gender'] = [ 0, 0 ]
				report[type]['student'] = { }
			reader = csv.DictReader(fin)
			for line in reader:
				type = GetType(line)
				g = line['Gender Code']
				email = line['Carthage E-mail']
				gpa = float(line['Cumulative GPA'])
				pgy = line['Planned Graduation Year']
				pgs = line['Planned Graduation Session Code']

				if type == None:
					continue
				#if file == files[0]:
				#	EventData[email] = [ g, { 'program': type, 'action': 'Add', 'when': base, 'gpa': gpa, 'pgy': pgy, 'pgs': pgs } ]
				if file == files[-1]:
					CurrentEmailAddresses[type].append(email)
					if pgy not in ExpGradData[type]:
						ExpGradData[type][pgy] = 1
					else:
						ExpGradData[type][pgy] += 1
					if type == Major_Literal:
						m1 = line['Major 1 Description']
						m2 = line['Major 2 Description']
						if m1 == Major or m2 == Major:
							if m1 == Major:
								m = m1 + '+' + m2
							if m2 == Major:
								m = m2 + '+' + m1
							if m in Pairings[type]:
								Pairings[type][m] += 1
							else:
								Pairings[type][m] = 1
					elif type == Minor_Literal:
						pass
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
	print('{:<25s} '.format('Major'), end='')
	print('{:<18s}'.format('Minor'), end='')
	print()
	print('{:<10s}'.format(''), end='')
	print('{:>5s}{:>5s}{:>6s}{:>8s} '.format('F', 'M', 'Total', 'Ratio'), end='')
	print('{:>5s}{:>5s}{:>6s}{:>8s}'.format('F', 'M', 'Total', 'Ratio'), end='')
	print()
	for report in data:
		print('{:<10s}'.format(report['name']), end='')
		f, m, r = ExtractGender(report[Major_Literal])
		print('{:>5d}{:>5d}{:>6d}{:>8.2f} '.format(f, m, f + m, r), end='')
		f, m, r = ExtractGender(report[Minor_Literal])
		print('{:>5d}{:>5d}{:>6d}{:>8.2f}'.format(f, m, f + m, r), end='')
		print()

def GetDelta(type, r1, r2, do_printing = True):
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
			if do_printing:
				print('Adds  - In', r2['name'],'compared to', r1['name'])
		else:
			r = r1
			direction = 'Drop'
			if do_printing:
				print('Drops - In', r1['name'],'compared to', r2['name'])
		something_printed = False
		for email in s:
			l = r[type]['student'][email]
			g = l['Gender Code']
			gpa = float(l['Cumulative GPA'])
			pgy = l['Planned Graduation Year']
			pgs = l['Planned Graduation Session Code']

			if email not in EventData:
				EventData[email] = [ g, { 'program': type, 'action': direction, 'when': r['name'], 'gpa': gpa, 'pgy': pgy, 'pgs': pgs } ]
			else:
				EventData[email].append({ 'program': type, 'action': direction, 'when': r['name'], 'gpa': gpa, 'pgy': pgy, 'pgs': pgs })
			if do_printing:
				print('{:<12s} {:<12s} {:<1s}'.format(l['Last Name'], l['First Name'], g), end='')
				print(' {:<4.3f}'.format(gpa), end='')
				print(' {:<26s}'.format(email), end='')
				print(' {:<6s}'.format(pgy), end='')
				print(' {:<6s}'.format(pgs), end='')
				print()
				something_printed = True
		if something_printed == False and do_printing:
			print('None')
		if counter == 0 and do_printing:
			print()
		counter += 1

def ChurnByMonth(data):
	print('--- MAJORS ---')
	print()
	for index in range(len(data) - 1):
		GetDelta(Major_Literal, data[index], data[index + 1])
		print()	
	print()
	print('--- MINORS ---')
	print()
	for index in range(len(data) - 1):
		GetDelta(Minor_Literal, data[index], data[index + 1])
		print()

def	ChurnByStudent(data):
	for index in range(len(data) - 1):
		GetDelta(Major_Literal, data[index], data[index + 1], False)
		GetDelta(Minor_Literal, data[index], data[index + 1], False)
	for email in EventData:
		if len(EventData[email]) > 1:
			ed = EventData[email]
			print('{:<2s}{:26s}'.format(ed[0], email), end='')
			d = ed[1]
			print('{:<8s}{:<6s} {:<6s} {:<5.3f} {:<4s} {:<2s}'.format(d['when'], d['program'], d['action'], d['gpa'], d['pgy'], d['pgs']))
			for d in ed[2:]:
				print('{:28s}{:<8s}{:<6s} {:<6s} {:<5.3f} {:<4s} {:<2s}'.format(' ', d['when'], d['program'], d['action'], d['gpa'], d['pgy'], d['pgs']))

def ExpectedGraduationReport():
	global ExpGradData
	types = list(ExpGradData.keys())
	types.sort()
	for type in types:
		print(type)
		print('{:<10s}{:>6s}'.format('Cohort', 'Count'))
		years = list(ExpGradData[type].keys())
		years.sort()
		for year in years:
			print('{:<10s}{:>6d}'.format(year, ExpGradData[type][year]))
		if type != types[-1]:
			print()

def DoEmailList(type):
	CurrentEmailAddresses[type].sort()
	for e in CurrentEmailAddresses[type]:
		print(e)

def GeneratePairings():
	global Pairings
	print('Pairings of Majors')
	majors = Pairings['Major']
	for p in majors:
		count = majors[p]
		m = p.split('+')
		print('{:<30s} {:<30s} {:3d}'.format(m[0], m[1], count))

if __name__ == "__main__":
	HandleCommandLine()
	files = EnumerateFolder(Folder)
	if len(files) == 0:
		exit('No CSV files found')
	data = ReadAllData(files)
	if DoPairing:
		GeneratePairings()
	if DoGenderData:
		MakeGenderPlot(data)
	if DoChurnByMonth:
		ChurnByMonth(data)
	if DoChurnByStudent:
		ChurnByStudent(data)
	if DoExpectedGraduation:
		ExpectedGraduationReport()
	if DoMinorEmail:
		DoEmailList(Minor_Literal)
	if DoMajorEmail:
		DoEmailList(Major_Literal)



	