#!/usr/bin/python2.6

from fractions import Fraction
import re
from math import *
import types
#import logging

mylog = open('/tmp/mylog', 'a+')

##################################
# Spiral of fifths (spoff) pitch representation functions
##################################

###################################
#
#	bb	b	N	#	x
#F	-14	-7	0	7	14
#C	-13	-6	1	8	15
#G	-12	-5	2	9	16
#D	-11	-4	3	10	17
#A	-10	-3	4	11	18
#E	-9	-2	5	12	19
#B	-8	-1	6	13	20
#
#####################################

#####################################
# Oooops! Check this against whiteboard
#	-14	-7	0	7	14
#0	dd1	d1	1st	a1	aa1
#1	dd5	d5	P5	a5	aa5
#2	d2	m2	M2	a2	aa2
#3	d6	m6	M6	a6	aa6
#4	d3	m3	M3	a3	aa3
#5	d7	m7	M7	a7	aa7
#6	dd4	d4	P4	a4	aa4
#
#####################################
#####################################
# 
#	-14	-7	0	7	14
#0		d1	1st	a1	
#1		d5	P5	a5	
#2	d2	m2	M2	a2	
#3	d6	m6	M6	a6	
#4	d3	m3	M3	a3	
#5	d7	m7	M7	a7	
#6	d4	P4	a4		
#
#####################################


naturals = {'F':0, 'C':1, 'G':2, 'D':3, 'A':4, 'E':5, 'B':6}
pitch_order = [3, 0, 4, 1, 5, 2, 6]
interval_order = [1, 5, 2, 6, 3, 7, 4]

intervalList = [0, 0, 2, 4, -1, 1, 3, 5]
intervalListP4 = [0, 0, 2, 4, 6, 1, 3, 5]

majorScale = [ 	{'interval': 2, 'divisions_per_semitone': 1, 'octave': 0},
		{'interval': 2, 'divisions_per_semitone': 1, 'octave': 0},
		{'interval': -5, 'divisions_per_semitone': 1, 'octave': 0},
		{'interval': 2, 'divisions_per_semitone': 1, 'octave': 0},
		{'interval': 2, 'divisions_per_semitone': 1, 'octave': 0},
		{'interval': 2, 'divisions_per_semitone': 1, 'octave': 0},
		{'interval': -5, 'divisions_per_semitone': 1, 'octave': 0} ]

minorScale = majorScale[5:] + majorScale[0:5]		#harmonic minor
#minorScale = harmonicMinorScale[0:6] + [{'interval': 7, 'divisions_per_octave': 1, 'octave': 0}], [{'interval': -5, 'divisions_per_octave': 1, 'octave': 0}], 
#modes???

##
# TODO Create functions to correctly map PG types onto python types eg. spoff_pitch
# 	see psycopg2.extensions.cursor new_type(val, cur) function
##

def musicxml2spoff(step, alter):
	if step == None:
		return None
	elif step == 'NULL':
		return 'NULL'
	else:
		return naturals[step] + (7*alter)

def python2sqlstring(py_var):
	if isinstance(py_var, types.StringTypes):
		return '\''+py_var+'\''
	elif py_var==None:
		return 'NULL'
	elif isinstance(py_var, list):
		return ' \'{ ' + ', '.join([python2sqlstring(item) for item in py_var]) + ' }\' '
	else:
		return str(py_var)
	#TODO more types here; recurse for list etc types

def clefSign2Number(clefSign):
	return ['F', 'C', 'G', 'percussion', 'TAB', 'none'].index(clefSign)

#def spoff2freq(spoff_pitch, divisions_per_octave = 12, temperament = 'equal', a_below_middle_c = 440):
	#what octave is A440?
	#calc low c for spoff_pitch['octave']
	#calc size of semitone: oct/dpo
	#calc pitch class ie from pitch chapter ( % 7z)
	#We assume a diatonic scale MMmMMMm and equal temperament
	#therefore M2 = 2 x m2
	#therefore we can work out how many semitones from the low-c to the pitch class
	#add or subtract number of semitones ( / 7z) - see pitch chapter
	#return freq

#def addInterval(source_note, interval):
#	"""Add an interval to a note, both expressed in spoff format
#
#	"""
#	source_note_pitch = source_note['pitch'] 
#	source_note_dps = ['divisions_per_semitone']
#	source_note_octave = source_note['octave'] 
#	interval_interval = interval['interval'] 
#	interval_dps = interval['divisions_per_semitone'] 
#	interval_octave = interval['octave'] 
#
	#is the % statement the wrong way round?
	#need to test this a bit more
	#time for some paper calculations
#	if source_note_dps < interval_dps and not (source_note_dps % interval_dps):
#		#return result in higher dps
#		result_pitch =  int(float(source_note_pitch) / source_note_dps * interval_dps) + interval_interval
#		result_octave = source_octave + interval_octave
#		return {'pitch': result_pitch, 'divisions_per_octave': interval_dps, 'octave': result_octave}

def addInterval(note, interval):
	noteFraction = Fraction(note['pitch'], note['divisions_per_semitone'])
	intervalFraction = Fraction(interval['interval'], interval['divisions_per_semitone'])
	newNoteFraction = noteFraction + intervalFraction
	newOctave = note['octave'] + interval['octave']
	#TODO: this doesn't account for when the interval takes us over the octave boundary. see below
	newNote = {'pitch': newNoteFraction.numerator, 'divisions_per_semitone': newNoteFraction.denominator, 'octave': newOctave}
	if lessThanPitch(note, newNote):
		#we have wrapped around
		newNote['octave'] = newNote['octave'] + 1
	
	return newNote
	

#def getInterval(source_note, dest_note):
	#"""Calculate the interval between 2 notes
	#
	#returns a dictionary containing the spoff_interval_type. The octave reveals any shift in octave in addition to that brought about by the interval. The direction will be +1 for up, -1 for down and 0 for unison"""
	
	#source_value = source_note['value']
	#source_octave = source_note['octave']
	#dest_value = dest_note['value']
	#dest_octave = dest_note['octave']
	
	#if (source_note['type'] != 'pitch') or (dest_note['type'] != 'pitch'):
		#interval_list = [None, None, None]
	#if source_octave == dest_octave:
		#if pitch_order[source_value % 7] < pitch_order[dest_value % 7]:
			#interval_list = [dest_value-source_value, 0, 1]
		#elif pitch_order[source_value % 7] > pitch_order[dest_value % 7]:
			#interval_list = [dest_value-source_value, 0, -1]
		#else:		#unison
			#interval_list = [0, 0, 0]
	#elif source_octave < dest_octave:
		#if pitch_order[source_value % 7] < pitch_order[dest_value % 7]:
			#interval_list = [dest_value-source_value, dest_octave-source_octave-1, 1]
		#elif pitch_order[source_value % 7] > pitch_order[dest_value % 7]:
			#interval_list = [dest_value-source_value, dest_octave-source_octave-1, 1]
		#else:		#octave up
			#interval_list = [0, dest_octave-source_octave-1, 1]
	#elif source_octave > dest_octave:
		#if pitch_order[source_value % 7] < pitch_order[dest_value % 7]:
			#interval_list = [source_value-dest_value, source_octave-dest_octave, -1]
		#elif pitch_order[source_value % 7] > pitch_order[dest_value % 7]:
			#interval_list = [source_value-dest_value, source_octave-dest_octave, -1]
		#else:		#octave down
			#interval_list = [0, source_octave-dest_octave, -1]
	#return {'source_work_id': source_note['work_id'],
		#'source_note_id': source_note['note_id'],
		#'dest_work_id': dest_note['work_id'],
		#'dest_note_id': dest_note['note_id'],
		#'value': interval_list[0],
		#'direction': interval_list[1],
		#'octave': interval_list[2]}

def getInterval(source_pitch, dest_pitch):
	if (source_pitch==None) or (dest_pitch==None):
		return None
	sourceNoteFraction = Fraction(source_pitch['pitch'], source_pitch['divisions_per_semitone'])
	destNoteFraction = Fraction(dest_pitch['pitch'], dest_pitch['divisions_per_semitone'])
	#take account of octaves
	source_pitch_octave_zero = dict(source_pitch)
	source_pitch_octave_zero['octave'] = 0
	dest_pitch_octave_zero = dict(dest_pitch)
	dest_pitch_octave_zero['octave'] = 0
	if lessThanPitch(source_pitch_octave_zero, dest_pitch_octave_zero):
		octave_less_than = 0
		octave_more_than = -1
	elif greaterThanPitch(source_pitch_octave_zero, dest_pitch_octave_zero):
		octave_less_than = -1
		octave_more_than = 0
	elif equatePitch(source_pitch_octave_zero, dest_pitch_octave_zero):
		octave_less_than = 0
		octave_more_than = 0
	else:
		return None
	if source_pitch['octave'] < dest_pitch['octave']:
		newNoteFraction = destNoteFraction - sourceNoteFraction		#TODO:. Check this please!
		return {'interval': newNoteFraction.numerator,
			'divisions_per_semitone': newNoteFraction.denominator,
			'octave': dest_pitch['octave'] - source_pitch['octave'] + octave_less_than}		#TODO:. Check again please!
	elif source_pitch['octave'] > dest_pitch['octave']:
		#dest is lower
		newNoteFraction = sourceNoteFraction - destNoteFraction		#TODO:. Check this please!
		return {'interval': newNoteFraction.numerator,
			'divisions_per_semitone': newNoteFraction.denominator,
			'octave': source_pitch['octave'] - dest_pitch['octave'] + octave_more_than}		#TODO:. Check again please!
	else:
		#in same octave
		if lessThanPitch(source_pitch, dest_pitch):
			#source_pitch is lower
			newNoteFraction = destNoteFraction - sourceNoteFraction		#TODO:. Check this please!
			return {'interval': newNoteFraction.numerator,
				'divisions_per_semitone': newNoteFraction.denominator,
				'octave': dest_pitch['octave'] - source_pitch['octave']}		#TODO:. Check again please!
		elif greaterThanPitch(source_pitch, dest_pitch):
			#dest is lower
			newNoteFraction = sourceNoteFraction - destNoteFraction		#TODO:. Check this please!
			return {'interval': newNoteFraction.numerator,
				'divisions_per_semitone': newNoteFraction.denominator,
				'octave': source_pitch['octave'] - dest_pitch['octave']}		#TODO:. Check again please!
		elif equatePitch(source_pitch, dest_pitch):
			#unison
			return {'interval': 0,
				'divisions_per_semitone': 1,
				'octave': 0}
		else:
			raise ValueError


#TODO fix this for higher dps
def lessThanPitch(source_pitch, dest_pitch):
	if (source_pitch==None) or (dest_pitch==None):
		return None
	elif dest_pitch['octave'] > source_pitch['octave']:
		return True
	elif dest_pitch['octave'] < source_pitch['octave']:
		return False
	elif pitch_order[dest_pitch['pitch'] % 7] > pitch_order[source_pitch['pitch'] % 7]:
		return True
	elif pitch_order[dest_pitch['pitch'] % 7] < pitch_order[source_pitch['pitch'] % 7]:
		return False
	elif (pitch_order[dest_pitch['pitch'] % 7] == pitch_order[source_pitch['pitch'] % 7]) and (pitch_order[dest_pitch['pitch'] / 7] > pitch_order[source_pitch['pitch'] / 7]):
		# ie same note class, one note is flatter than the other
		return True
	else:
		return False

#TODO fix this for higher dps
def greaterThanPitch(source_pitch, dest_pitch):
#sp = 4,1,5	dp = 2,1,5
	if (source_pitch==None) or (dest_pitch==None):
		return None
#	elif dest_pitch['octave'] > source_pitch['octave']:
#		return True
#	elif dest_pitch['octave'] < source_pitch['octave']:
#		return False
	elif source_pitch['octave'] > dest_pitch['octave']:
		return True
	elif source_pitch['octave'] < dest_pitch['octave']:
		return False
	elif pitch_order[source_pitch['pitch'] % 7] > pitch_order[dest_pitch['pitch'] % 7]:
		return True
	elif pitch_order[source_pitch['pitch'] % 7] < pitch_order[dest_pitch['pitch'] % 7]:
		return False
	elif (pitch_order[dest_pitch['pitch'] % 7] == pitch_order[source_pitch['pitch'] % 7]) and (pitch_order[source_pitch['pitch'] / 7] > pitch_order[dest_pitch['pitch'] / 7] ):
		# ie same note class, one note is sharper than the other
		return True
	else:
		return False
#TODO change this to take account of divs per semitone
def equatePitch(source_pitch, dest_pitch):
	if (source_pitch==None) or (dest_pitch==None):
		return None
	elif (dest_pitch['octave'] == source_pitch['octave']) and (dest_pitch['pitch'] == source_pitch['pitch']):
		return True
	else:
		return False

#TODO change this to take account of divs per semitone
def approxEquatePitch(source_pitch, dest_pitch):
	if (source_pitch==None) or (dest_pitch==None):
		return None
	elif dest_pitch['pitch'] == source_pitch['pitch']:
		return True
	else:
		return False
################################
## Time functions
##
################################

def greaterThanTime(t1, t2):
	fraction1 = Fraction(t1['crotchet_numerator'], t1['crotchet_denominator'])
	fraction2 = Fraction(t2['crotchet_numerator'], t2['crotchet_denominator'])
	return fraction1>fraction2

def greaterThanOrEqualToTime(t1, t2):
	fraction1 = Fraction(t1['crotchet_numerator'], t1['crotchet_denominator'])
	fraction2 = Fraction(t2['crotchet_numerator'], t2['crotchet_denominator'])
	return fraction1>=fraction2

def lessThanTime(t1, t2):
	fraction1 = Fraction(t1['crotchet_numerator'], t1['crotchet_denominator'])
	fraction2 = Fraction(t2['crotchet_numerator'], t2['crotchet_denominator'])
	return fraction1<fraction2

def lessThanOrEqualToTime(t1, t2):
	fraction1 = Fraction(t1['crotchet_numerator'], t1['crotchet_denominator'])
	fraction2 = Fraction(t2['crotchet_numerator'], t2['crotchet_denominator'])
	return fraction1<=fraction2

def equateTime(t1, t2):
	fraction1 = Fraction(t1['crotchet_numerator'], t1['crotchet_denominator'])
	fraction2 = Fraction(t2['crotchet_numerator'], t2['crotchet_denominator'])
	return fraction1==fraction2



def addDuration(location, duration, beats=4, divisionsPerBeat=8):
	sourceBar = location['bar']
	sourceBeat = location['beat']
	sourceDiv = location['division']
	durBars = duration['bar']
	durBeats = duration['beat']
	durDivs = duration['division']
	
	overflowBeats = (sourceDiv + durDivs) / divisionsPerBeat
	newDivisions = (sourceDiv + durDivs) % divisionsPerBeat
	overflowBars = (sourceBeat + durBeats + overflowBeats) / beats
	newBeats = (sourceBeat + durBeats + overflowBeats) % beats
	newBars = sourceBar + durBars + overflowBars

	return {'bar': newBars, 'beat': newBeats, 'division': newDivisions}

def getSimultaneous(source_note, dest_table):
	"""Find notes which are simultaneous with the given note

	returns a list of score_notes which overlap in time with the source_note"""
	
	plan = plpy.prepare("""	SELECT * FROM %(tablename)s
				WHERE %(tablename)s.location """)

#def text2interval(text):
	#text in the form:
	# '1+m3rd' - an octave and a minor 3rd
	# or 'm10th' - as above
	#regex = re.compile('([0-9]+\+)?([MmPp]?|[AaDd]*)([0-9]+)(st|nd|rd|th)')
	#result = regex.search(text)
	#if result:
		#interval_type = result.group(2)
		#interval_number = result.group(3)
		#octave = result.group(1) if result.group(1) else 0
		#octave = octave + (interval_number / 7)
		#should m/M/P etc be optional as per wikipedia page?
		#interval = interval_order[int(interval_number)%7]
		#if interval_type
	#else:
#1	raise ValueError

#need 2 more interval operators:
#	interval ~= interval -> True|False :: whether interval is in the same class ie. m3, m10, m17
#	interval #= interval -> True|False :: whether intervals are in the same interval class ie. M3, m3, M10, m10 are all scalar 3rds
#also need a few utility functions:
#	text2interval("string") -> interval :: converts string to a interval eg. "1+M3rd" -> (4,1,1)
#	interval2text(interval) -> "string" :: converts interval to a string eg. 
#	scale("string") -> pitch[] :: returns an array of pitches making a single octave of the desired scale
#	pitch <- pitch[] -> True|False :: whether pitch is an element of the array of pitches
#	pitch <~ pitch[] -> True|False :: whether pitch is element of the array of pitches ignoring octaves
#	spoff_time <- spoff_time[] -> True|False :: 

def text2interval(text):
	regex = re.compile('([0-9]*)\+?([MmPp]?|[Aa]*|[Dd]*)([0-9]+)(st|nd|rd|th)?')
	matches = regex.match(text)
	
	octave = int(matches.group(1)) if matches.group(1) else 0
	alter = matches.group(2) if matches.group(2) else ''
	type = int(matches.group(3))
	
	octave = octave + (type / 8)		#8 notes in a diatonic octave
	interval_class = type % 8
	modifier = 0
	
	if (interval_class in [2, 3, 6, 7]):
		if ('M' in alter):
		#Major
			modifier = 0
		elif ('m' in alter):
		#minor
			modifier = -7
		elif ('a' in alter) or ('A' in alter):
		#augmented 
			modifier = 7 * len(alter)
		elif ('d' in alter) or ('D' in alter):
		#diminished
			modifier = -7 * len(alter) -7
	elif (interval_class in [0, 1, 4, 5]):
		if ('P' in alter) or ('p' in alter):
		#perfect
			modifier = 0
		if ('a' in alter) or ('A' in alter):
		#augmented 
			modifier = 7 * len(alter)
		elif ('d' in alter) or ('D' in alter):
		#diminished
			modifier = -7 * len(alter)
	else:
		raise ValueError

	return {'interval': intervalList[interval_class] + modifier, 'divisions_per_semitone': 1, 'octave': octave}

def interval2text(interval):
# Whoa! should it really be called divisions per semitone when we are talking about intervals?
	#will this work? can/how does the modulo operator work on Fractions?
	#what about div_per_s > 1 ??
	#continuing assuming that dps = 1 
	interval_string = str(interval['octave']) + '+'
	spoff_interval_class = interval['interval'] % 7
	spoff_modifier = interval['interval'] / 7
	interval_class = intervalListP4.index(spoff_interval_class)	#+1 ???
	if (interval_class in [2, 3, 6, 7]):
		if (-2 <= spoff_modifier <= 1):
			interval_string = interval_string + ['d', 'm', 'M', 'A'][spoff_modifier+2] + str(interval_class)
		elif ( spoff_modifier < -2):
			interval_string = interval_string + ('A' * spoff_modifier) + str(interval_class)
		elif (spoff_modifier > 1):
			interval_string = interval_string + ('d' * abs(spoff_modifier)) + str(interval_class)
	elif (interval_class == 4):
		if (spoff_modifier == -1):
			interval_string = interval_string + 'P' + str(interval_class)
		elif (spoff_modifier < -1):
			interval_string = interval_string + ('d' * abs(spoff_modifier+1)) + str(interval_class)
		elif (spoff_modifier > -1):
			interval_string = interval_string + ('A' * abs(spoff_modifier+1)) + str(interval_class)
	elif (interval_class == 5):
		if (spoff_modifier == 0):
			interval_string = interval_string + 'P' + str(interval_class)
		elif (spoff_modifier < 0):
			interval_string = interval_string + ('d' * abs(spoff_modifier)) + str(interval_class)
		elif (spoff_modifier > 0):
			interval_string = interval_string + ('A' * abs(spoff_modifier)) + str(interval_class)
	elif (interval_class in [0,1]):
		#unison or octave?
		interval_string = interval_string + 'P1'
	else:
		#failure
		raise ValueError
	
	return interval_string

def scale(text):
	regex = re.compile('([AaBbCcDdEeFfGg][b#]?)([Mm])')
	matches = regex.match(text)
	keynote = text2pitch(matches.group(1))
	type = matches.group(2)
	if (type == 'M'):
		scale = majorScale
	elif (type == 'm'):
		scale = minorScale		#assumes harmonic minor
	else:
		raise ValueError
	pitchArray = [keynote]
	for interval in scale:
		pitchArray.append(addInterval(pitchArray[-1], interval))

	return pitchArray
		
def elementOfPitchArray(testPitch, pitchArray):
	for pitch in pitchArray:
		if equatePitch(testPitch, pitch):
			return True
	return False

def approxElementOfPitchArray(testPitch, pitchArray):
	for pitch in pitchArray:
		if approxEquatePitch(testPitch, pitch):
			return True
	return False

def pitch2text(pitch):
	#TODO extend to pitches where dps>1
	spoffPitch = pitch['pitch']
	dps = pitch['divisions_per_semitone']
	spoffPitchClass = ((spoffPitch + ((spoffPitch % dps) *7)) / dps) %7
	#accidental = spoffPitch / (7*dps) + (spoffPitch % dps)
	accidental = (spoffPitch - (spoffPitchClass * dps) ) / 7
	pitchString = naturals.keys()[naturals.values().index(spoffPitchClass)]
	pitchFraction = Fraction(spoffPitch, dps)
	octave = str(pitch['octave'])
	if dps > 2:
		pitchString = ''.join([pitchString, str(abs(accidental)), '/', str(dps), '#' if pitchFraction.numerator > 0 else 'b', octave])
	elif dps == 2:
		if spoffPitch > (spoffPitchClass * dps):
			accidentalSemitone = '#'
			accidentalQuartertone = '+'
		else:
			accidentalSemitone = 'b'
			accidentalQuartertone = 'd'
		pitchString = ''.join([pitchString, (abs(accidental) %2)*accidentalQuartertone, (abs(accidental) /2)*accidentalSemitone, octave])
	elif dps == 1:
		if accidental >0:
			accidentalSign = '#'
		elif accidental <0:
			accidentalSign = 'b'
		else:
			accidentalSign = ''
		pitchString = ''.join([pitchString, abs(accidental) / dps * accidentalSign, octave])
	else:
		raise ValueError

	return pitchString


def text2pitch(text):
	#TODO extend to pitches with sesqui- and semi- intervals ie. dps>1
	regex = re.compile('([a-gA-G])([#b])*(-?[0-9]*)')
	matches = regex.match(text)
	pitchClass = naturals[matches.group(1).upper()]
	accidental = matches.group(2) if matches.group(2) else ''
	octave = int(matches.group(3)) if matches.group(3) else 0
	if ('#' in accidental):
		#sharp
		alter = 7 * len(accidental)
	elif ('b' in accidental):
		#flat
		alter = -7 * len(accidental)
	else:
		alter = 0

	return {'pitch': pitchClass + alter, 'divisions_per_semitone': 1, 'octave': octave}

#####################################
# 
#	-14	-7	0	7	14
#0		d1	1st	a1	
#1		d5	P5	a5	
#2	d2	m2	M2	a2	
#3	d6	m6	M6	a6	
#4	d3	m3	M3	a3	
#5	d7	m7	M7	a7	
#6	d4	P4	a4		
#
#####################################

def equateIntervalType(interval1, interval2):
	#  ~= ignoring octaves eg. M3 ~= M10 -> True
	if (interval1==None) or (interval2==None):
		return False
	#TODO check this for more exotic intervals and dps
	if Fraction(interval1['interval'],interval1['divisions_per_semitone']) == Fraction(interval2['interval'],interval2['divisions_per_semitone']):
		return True
	else:
		return False

def equateIntervalClass(interval1, interval2):
	#  #= eg. all thirds are in the same class m3 #= M17 -> True
	if (interval1==None) or (interval2==None):
		return False
	#TODO check this for more exotic intervals and dps
	if Fraction(interval1['interval'],interval1['divisions_per_semitone']) %7 == Fraction(interval2['interval'],interval2['divisions_per_semitone']) %7:
		return True
	else:
		return False

def equateInterval(interval1, interval2):
	if (interval1==None) or (interval2==None):
		return False
	#TODO check this for more exotic intervals and dps
	if (Fraction(interval1['interval'],interval1['divisions_per_semitone']) == Fraction(interval2['interval'],interval2['divisions_per_semitone'])) and (interval1['octave'] == interval2['octave']):
		return True
	else:
		return False

############ 
# output lilypond
###########
def spoff_pitch2lily(pitch):
	if pitch==None:
		return ''
	pitchList = pitch.strip('()').split(',')
	spoffPitch = int(pitchList[0])
	dps = int(pitchList[1])
	spoffPitchClass = ((spoffPitch + ((spoffPitch % dps) *7)) / dps) %7
	#accidental = spoffPitch / (7*dps) + (spoffPitch % dps)
	accidental = (spoffPitch - (spoffPitchClass * dps) ) / 7
	pitchString = naturals.keys()[naturals.values().index(spoffPitchClass)].lower()
	pitchFraction = Fraction(spoffPitch, dps)
	# Middle C: C4 in spoff/musicxml, c' in lilypond
	lilyOctave = (int(pitchList[2]) -3)
	octave = lilyOctave * '\'' if lilyOctave >=0 else abs(lilyOctave)*','
	if dps > 2:
		raise ValueError #TODO implement something here!
		# see second bullet at http://lilypond.org/doc/v2.12/Documentation/topdocs/NEWS
	elif dps == 2:
		if spoffPitch > (spoffPitchClass * dps):
			accidentalSemitone = 'is'
			accidentalQuartertone = 'ih'
		else:
			accidentalSemitone = 'es'
			accidentalQuartertone = 'eh'
		pitchString = ''.join([pitchString, (abs(accidental) %2)*accidentalQuartertone, (abs(accidental) /2)*accidentalSemitone, octave])
	elif dps == 1:
		if accidental >0:
			accidentalSign = 'is'
		elif accidental <0:
			accidentalSign = 'es'
		else:
			accidentalSign = ''
		pitchString = ''.join([pitchString, abs(accidental) / dps * accidentalSign, octave])
	else:
		raise ValueError

	return pitchString

def reducePow2(number):
	#reduces number to a list of powers of 2. The first in the list can be used as the note duration class with the length of the remaining list determining the number of dots. sort of but no quite...
	residual = number
	integralList = []
	while residual != 0:
		#modf returns a tuple of (fractional_part, integral_part)
		pow2_fractional, pow2_integral = modf(log(residual, 2))
		integralList.append(pow2_integral)
		residual = residual - 2**pow2_integral
	return integralList
	

def spoff_time2lily(time):
	#spoff_score_time (along with musicxml) represents time in divisions of a crotchet. Lilypond represents time as divisions of a whole note denominator
	if time==None:
		return ''
	timeList = plpy2list(time)
	timeFraction = Fraction(timeList[0], timeList[1])
	#check if fraction denominator is a power of 2. If not, duration is dotted
	#TODO check this for musical tuples. Maybe deal with musical tuples in the note_group section
	pow2ListNumerator = reducePow2(timeFraction.numerator)
	pow2ListDenominator = reducePow2(timeFraction.denominator)
	if (pow2ListNumerator == []) or (pow2ListDenominator == []):
		return ''
	else:
		durationClass = 4*Fraction(int(2**pow2ListNumerator.pop(0)), int(2**pow2ListDenominator.pop(0)))**-1
		dotcount = len(pow2ListNumerator) + len(pow2ListDenominator)
		return str(durationClass) + ('.' * dotcount)
	
def mxmlKeySig2lily(mxml_key):
	spoff_key = mxml_key + 1
	pitch_class = naturals.keys()[naturals.values().index(spoff_key%7)].lower()
	accidentalCount = spoff_key / 7
	# flats and sharps
	accidental = (-accidentalCount)*'es' if accidentalCount < 0 else accidentalCount*'is'
	return pitch_class + accidental 

def plpy2list(valuestring):
	# '{2,3,5,676}'
	# Make sure we actually got a string!
	if not isinstance(valuestring, str):
		return valuestring
	
	#Eurggh too clever
	return [int(val) if val != '' else 0 for val in valuestring.strip('{}()').split(',')]
	#return [int('0'+val) for val in valuestring.strip('{}()').split(',')]

def doc2lilypond(doc, plpy):
#def doc2lilypond(doc):
	""" Takes a data structure (defined below) and returns a text string of lilypond markup
	
	Data Structure:
	
	GD {
		doc {
			"textUnderList" {
				part_id {
					voice [
						"melodic_intervals",
						"chord_names", ...]
			"barGraphList" [
				"MIDI_velocity",
				"ioi", ... ]
			... #other display methods
			"noteData" {
				work_id {
					note_id {
						"pitch": (0,1,0), "onset": (0,1,2), ... #rest of score_note type
						"melodic_intervals": 5, "MIDI_velocity": 99, "ioi": 32 ... }
					...}
				...}
		...}
	}"""

	#get group data
	
	
						#> if unsuccessful output a skip to the lyric
					# as above for each bargraph entry, etc
	
	# collect all the lists into one big string including headers
	
	# Lilypond file structure - don't forget to escape the \'s: \ -> \\
	# \book {							;;one per document
	# 	\score {						;;one per work
	#		\new Staff = "part_id" << 			;;one per part
	#			\new Voice {				;;one per voice
	#			}
	#			\addLyrics {				;;one per data list
	#			}
	#		>>
	#	}
	# }

	groupQuery = plpy.prepare("select ng.id, ng.type, ng.comment, ng.value from note_groups as ng, (select note_group_id from note_groups__score_notes where score_note_note_id = $1 and score_note_work_id = $2) as ngid where ng.id = ngid.note_group_id;", ["int", "int"])
	in_chord = False
	keysig = None
	clef = None
	time = None
	tieString = ''
	inTie = False
	startTie = False
	endTie = False
	slurString = ''
	#previousNote = {'onset': {'crotchet_numerator': 0, 'crotchet_denominator':1}}		#dummy note. Is this dangerous?
	#previousNote = ['', {'onset': '(0,1)'}]		#dummy note. Is this dangerous?
	previousChord = False
	currentChord = False
	chordEndString  = ''
	chordStartString = ''
	textUnderLineNames = None
	textUnderLineDict = {}
	barGraphLineNames = None
	barGraphLineDict = {}
	lineGraphLineNames = None
	lineGraphLineDict = {}
	lilyList = ["""\\version "2.12.1"

	\pointAndClickOff
	valueboxheight = 10
	valueboxwidth = 1
	% #(define-markup-command (valuebox layout props value) (number?)
	%	(interpret-markup layout props (markup ( #:rounded-box ( #:with-color 'white #:filled-box #'(0 . 5) #'(0 . \\valueboxheight) #0 )))))
	#(define-markup-command (valuebox layout props val) (number?)
              "Draws 2 boxes - one containing val as text, one containing val as a line graph - in a column"
                 (interpret-markup layout props
                  (markup  
                   #:center-column 
                    (#:override '(box-padding . 0.1)
                    #:rounded-box 
                     (markup #:override '(font-size . -5) 
                      (format #f "~$" val))
                       #:override '(box-padding . 0.1)
                        #:rounded-box 
                         (#:combine
                          (#:combine
                           #:with-color (x11-color 'white)  #:filled-box `(0 . ,valueboxwidth) `(0 . ,valueboxheight) 0 
                            ;; #:with-color (x11-color 'pink)  #:filled-box `(0 . ,valueboxwidth) `(,(/ valueboxheight 2) . ,(+ 5 val)) 0 )
                            #:with-color (x11-color 'blue)  #:filled-box `(0 . ,valueboxwidth) `(0 . ,(* 8 val)) 0 )
                             ;; #:translate `(-0.1 . ,(/ valueboxheight 2)) #:draw-line `(,(+ 0.2 valueboxwidth) . 0)) 
                             #:translate `(-0.5 . 0) #:draw-line `(,(+ 1 valueboxwidth) . 0)) 
                    ))))
 
linegraphboxheight = 10
linegraphboxwidth = 5
linegraphscalefactor = 1
linegraphbias = 0

#(define (pslines prev_x x_inc y_list)
  (if (> (length y_list) 0)
   (format #f "~$ ~$ ~a~a" (exact->inexact (+ prev_x x_inc)) (* linegraphscalefactor (+ (car y_list) linegraphbias)) "lineto\n" (pslines (+ prev_x x_inc) x_inc (cdr y_list)))
   ""
   ))

#(define (generate-ps y_list)
  (format #f "~$ ~$ ~a~a~a" '0 (* linegraphscalefactor (+ (car y_list) linegraphbias)) "moveto\n" (pslines '0 (/ linegraphboxwidth (- (length y_list) 1)) (cdr y_list)) "stroke"))

#(define-markup-command (linegraphbox layout props y_list) (list?)
              "draws a line graph from  a list of values in fixed size box"
                 (interpret-markup layout props
                  (markup
		   (#:rounded-box
		     (#:combine
		     #:with-color (x11-color 'white) #:filled-box `(0 . ,linegraphboxwidth) `(0 . ,linegraphboxheight) 0
		     #:with-color (x11-color 'red) #:postscript (generate-ps y_list )
		     )))))
	
		#(define (startbracket x) (
	 (ly:context-set-property 'Voice textval $x)))

	%%#(define-markup-command (stopbracket layout props val)(number?)
	%%   (interpret-markup layout props (markup textval)))
	#(define-markup-command (stopbracket layout props val) (string?)
	  (interpret-markup layout props (markup #:ly:context-property 'textval 'Voice)))
	   \\layout {
	    \\context {
	     \\Voice
	      \\consists "Horizontal_bracket_engraver"
	    }
	   }
	  \\paper { ragged-right = ##f } \n\n
"""]


	lilyList.append('\\book {\n')
	mylog.write('doc2lilypond: itervalues 1\n')
	mylog.flush()
	for work in doc['noteData'].iterkeys():
		lilyList.append('\t\\score { <<\n')
		partSet = set( [note['part_id'] for note in doc['noteData'][work].itervalues()] )
		mylog.write('doc2lilypond: partSet: %s\n' % str(partSet))
		mylog.flush()
		for part_id in partSet:
			mylog.write('doc2lilypond: part ID: %s\n' % part_id)
			mylog.flush()
			lilyList.append('\t\t \\new Staff = \"%s\" \n <<' % (part_id))
			voiceSet = set( [note['voice'] for note in doc['noteData'][work].itervalues()] )
			mylog.write('doc2lilypond: voiceSet: %s\n' % str(voiceSet))
			mylog.flush()
			for voice in voiceSet:
				mylog.write('doc2lilypond: voice: %d\n' % voice)
				mylog.flush()

				# Check if current part/voice combo has any lyric lines to add.
				# If so, set up necessary variables to store them in.
				if 'textUnderList' in doc:
					if part_id in doc['textUnderList']:
						if voice in doc['textUnderList'][part_id]:
							textUnderLineNames = doc['textUnderList'][part_id][voice]
							for textUnderLine in textUnderLineNames:
								textUnderLineDict[textUnderLine] = []

				if 'barGraphList' in doc:
					if part_id in doc['barGraphList']:
						if voice in doc['barGraphList'][part_id]:
							barGraphLineNames = doc['barGraphList'][part_id][voice]
							for barGraphLine in barGraphLineNames:
								barGraphLineDict[barGraphLine] = []
				if 'lineGraphList' in doc:
					if part_id in doc['lineGraphList']:
						if voice in doc['lineGraphList'][part_id]:
							lineGraphLineNames = doc['lineGraphList'][part_id][voice]
							for lineGraphLine in lineGraphLineNames:
								lineGraphLineDict[lineGraphLine] = []
				noteStringList = []
				textUnderStringList = []
				barGraphStingList = []
				# whoah! Exxxtreeme Python! for each note in current part and voice, sorted by onset time
				noteList = [noteTuple for noteTuple in doc['noteData'][work].iteritems() if noteTuple[1]['part_id']==part_id and noteTuple[1]['voice']==voice]
				mylog.write('doc2lilypond: itervalues 4\n')
				mylog.flush()
				mylog.write(str(noteList))
				mylog.flush()
				noteList.sort(key=lambda note: Fraction(int(note[1]['onset'].strip('()').split(',')[0]), int(note[1]['onset'].strip('()').split(',')[1])))
				#mylog.write(str(noteList)+'\n')
				mylog.write('noteList length: %s\n' % len(noteList))
				mylog.flush()
				lilyList.append('\t\t\t {\n')
				for note in noteList:
					mylog.write('doc2lilypond: noteid: %d, %s\n' % (note[0], str(note[1])))
					mylog.flush()
					currentChord = False
					noteGroupList = plpy.execute(groupQuery, [note[0], work])
					#noteGroupList = []
					for noteGroup in noteGroupList:
						if noteGroup == None:
							continue
						mylog.write('doc2lilypond: noteid: %d, noteGroup: %s\n' % (note[0], noteGroup['type']))
						mylog.write('Calling plpy2list with '+str(noteGroup['value'])+'\n')
						mylog.flush()
						valueList = plpy2list(noteGroup['value'])
						mylog.flush()
						if 'key' in noteGroup['type']:
							if (keysig == None) or (keysig != valueList):
								keyString = mxmlKeySig2lily(valueList[0])
								#keyString = naturals.keys()[naturals.values().index(valueList[0])].lower()
								#TODO: properly deal with modes
								mode = 'major'
								lilyList.append(' \\key ' + keyString + ' \\' + mode + ' ')
								keysig = valueList
						elif 'clef' in noteGroup['type']:
							if (clef == None) or (clef != valueList):
								if valueList == [0,4]:
									lilyList.append(' \\clef bass ')
									clef = valueList
								elif valueList == [2,2]:
									lilyList.append(' \\clef treble ')
									clef = valueList
								else:
									lilyList.append(' ;unknown clef %s\n' % str(valueList))
									clef = 'unknown'
						if 'time' in noteGroup['type']:
							if (time == None) or (valueList != time):
								lilyList.append(' \\time %d/%d ' % (valueList[0], valueList[1]))
								time = valueList

						if 'tie' in noteGroup['type']:
							#TODO get value as a list
							if valueList[0] == int(note[0]):
								tieString = ' ~ '
								startTie = True
								endTie = False
							else:
								startTie = False
								endTie = True

						if 'slur' in noteGroup['type']:
							#TODO get value as list
							if valueList[0] == note[0]:
								#we are starting a slur
								slurString = ' ( ' 	#Spaces or no spaces?
							if valueList[1] == note[0]:
								#we are ending a slur
								slurString = ' ) '	#Spaces or no spaces?

						if 'chord' in noteGroup['type']:
							currentChord = noteGroup['id']	

						#TODO add code for slurs, ties, tuplets
								
					#TODO get the order right! output note before or after '>' or '<'

					#Are we in a tie?
					inTie = any(['tie' in x['type'] for x in noteGroupList])
					if currentChord and not previousChord:
						# start a chord, previous notes not in chord 
						chordStartString = ' < '
						durationString = ''
						chordEndString = ''
						if textUnderLineNames != None and (startTie or not inTie):
							for textUnderLine in textUnderLineNames:
								textUnderLineValue = note[1].get(textUnderLine, '')
								textUnderLineDict[textUnderLine].append('\\markup {\\column {')
								# The order of lines has to be reversed for the column
								# to be the right way up, so we'll just build a list of
								# stings to use later
								textUnderLineStrings = \
								  { textUnderLine: [ ' '.join(('\\tiny %s' % str(x) for x in textUnderLineValue)) ] }
								mylog.write("Starting chord. textUnderLineStrings="+str(textUnderLineStrings[textUnderLine])+'\n')
								mylog.flush()
						#output bargraph here
						if barGraphLineNames != None:
							for barGraphLine in barGraphLineNames:
								barGraphLineValue = note[1].get(barGraphLine, None)
								valuebox = ' \\valuebox #%s ' % str(barGraphLineValue) if barGraphLineValue != None else '{}'
								barGraphLineDict[barGraphLine].append(' \\markup %s ' % valuebox)
						#output linegraph here
						if lineGraphLineNames != None:
							for lineGraphLine in lineGraphLineNames:
								lineGraphLineValue = note[1].get(lineGraphLine, [])
								lineGraphValueString = [str(x) for x in lineGraphLineValue]
								linegraphbox = ' \\linegraphbox #\'(%s) ' % ' '.join(lineGraphValueString) if lineGraphLineValue != [] else '{}'
								lineGraphLineDict[lineGraphLine].append(' \\markup %s ' % linegraphbox)

	
					elif currentChord and previousChord:
						if currentChord == previousChord:
							#continuation of a chord
							#pass
							chordStartString = ''
							durationString = ''
							chordEndString = ''
							if textUnderLineNames != None and (startTie or not inTie):
								for textUnderLine in textUnderLineNames:
									textUnderLineValue = note[1].get(textUnderLine, '')
									textUnderLineStrings[textUnderLine].append(' '.join(('\\tiny %s' % str(x) for x in textUnderLineValue)))
									mylog.write("Chord continues. textUnderLineStrings="+str(textUnderLineStrings[textUnderLine])+'\n')
									mylog.flush()

						else:
							# end a chord, start a new chord
							chordStartString = ' >%s < ' % spoff_time2lily(previousDuration)
							durationString = ''
							chordEndString = ''
							if textUnderLineNames != None and (startTie or not inTie):
								for textUnderLine in textUnderLineNames:
									textUnderLineValue = note[1].get(textUnderLine, '')
									textUnderLineStrings.append(' '.join(('\\tiny %s' % str(x) for x in textUnderLineValue)))
									mylog.write("End of chord; starting new. textUnderLineStrings="+str(textUnderLineStrings[textUnderLine])+'\n')
									mylog.flush()
									textUnderLineDict[textUnderLine].append(
									  ' '.join( [ '\\line{ %s } ' % str(x) for x in \
									       reversed(textUnderLineStrings[textUnderLine]) ] ))
									textUnderLineStrings[textUnderLine]=[]
									textUnderLineDict[textUnderLine].append('}} \\markup {\\column { ')
							#output bargraph here
							if barGraphLineNames != None:
								for barGraphLine in barGraphLineNames:
									barGraphLineValue = note[1].get(barGraphLine, None)
									valuebox = ' \\valuebox #%s ' % str(barGraphLineValue) if barGraphLineValue != None else '{}'
									barGraphLineDict[barGraphLine].append(' \\markup %s ' % valuebox)
							#output linegraph here
							if lineGraphLineNames != None:
								for lineGraphLine in lineGraphLineNames:
									lineGraphLineValue = note[1].get(lineGraphLine, [])
									lineGraphValueString = [str(x) for x in lineGraphLineValue]
									linegraphbox = ' \\linegraphbox #\'(%s) ' % ' '.join(lineGraphValueString) if lineGraphLineValue != [] else '{}'
									lineGraphLineDict[lineGraphLine].append(' \\markup %s ' % linegraphbox)


					elif previousChord and not currentChord:
						#end a chord
						chordStartString = ' >%s ' % spoff_time2lily(previousDuration)
						durationString = spoff_time2lily(note[1]['duration'])
						chordEndString = ''
						if textUnderLineNames != None and (startTie or not inTie):
							for textUnderLine in textUnderLineNames:
								textUnderLineValue = note[1].get(textUnderLine, '')
								textUnderLineStrings[textUnderLine].append(' '.join(('\\tiny %s' % str(x) for x in textUnderLineValue)))
								mylog.write("End of chord. textUnderLineStrings="+str(textUnderLineStrings[textUnderLine])+'\n')
								mylog.flush()
								textUnderLineDict[textUnderLine].append(
									  ' '.join( [ '\\line{ %s } ' % str(x) for x in \
									       reversed(textUnderLineStrings[textUnderLine]) ] ))
								textUnderLineStrings[textUnderLine]=[]
								textUnderLineDict[textUnderLine].append(' }} ')

					else:
						#previousChord and currentChord are false
						#we are not in a chord
						chordStartString = ''
						durationString = spoff_time2lily(note[1]['duration'])
						chordEndString = ''
						#add lyric lines for text under 
						if 'rest' in note[1]['type']:
							pass
						else:
							if textUnderLineNames != None and (startTie or not inTie):
								for textUnderLine in textUnderLineNames:
									textUnderLineValue = note[1].get(textUnderLine, '')
									textUnderLineDict[textUnderLine].append('\\markup {%s}' % ' '.join(('\\tiny %s' % str(x) for x in textUnderLineValue)))
							#output bargraph here
							if barGraphLineNames != None and (startTie or not inTie):
								for barGraphLine in barGraphLineNames:
									barGraphLineValue = note[1].get(barGraphLine, None)
									valuebox = ' \\valuebox #%s ' % str(barGraphLineValue) if barGraphLineValue != None else '{}'
									barGraphLineDict[barGraphLine].append(' \\markup %s ' % valuebox)
							#output linegraph here
							if lineGraphLineNames != None and (startTie or not inTie):
								for lineGraphLine in lineGraphLineNames:
									lineGraphLineValue = note[1].get(lineGraphLine, [])
									lineGraphValueString = [str(x) for x in lineGraphLineValue]
									linegraphbox = ' \\linegraphbox #\'(%s) ' % ' '.join(lineGraphValueString) if lineGraphLineValue != [] else '{}'
									lineGraphLineDict[lineGraphLine].append(' \\markup %s ' % linegraphbox)


						
					#NB: we only output a barGraph or a lineGraph on the first note of a chord which shows up. It will not necessarily be the highest or lowest. It will be the first note which is returned by the query. It might be useful to consider using an 'order by pitch' clause in queries to ensure consistancy.
					# output note here!!
					if 'pitch' in note[1]['type']:
						noteString = spoff_pitch2lily(note[1]['pitch'])
					elif 'rest' in note[1]['type']:
						noteString = 'r'

					else:
						noteString = 'unknown type at %s' % note[0]
					lilyList.extend([' ', chordStartString, noteString, durationString, slurString, tieString, chordEndString ])
					#previousNote = note
					previousChord = currentChord
					previousDuration = note[1]['duration']
					tieString = ''
					slurString = ''
					#experimental bit follows!!
					chordStartString = ''
					chordEndString = ''
					endTie = False
				#check for an unfinished chord
				#lilyList.extend(noteStringList)	
				if currentChord:
					lilyList.append(' >%s ' % spoff_time2lily(previousDuration))
					if textUnderLineNames != None:
						for textUnderLine in textUnderLineNames:
							mylog.write("Unfinished chord: textUnderLineStrings=%s\n"%str(textUnderLineStrings[textUnderLine]))
							mylog.flush()
							textUnderLineDict[textUnderLine].append(
									  ' '.join( [ '\\line{ %s } ' % str(x) for x in \
									       reversed(textUnderLineStrings[textUnderLine]) ] ))
							textUnderLineDict[textUnderLine].append('}} %% %s\n\t\t' % textUnderLine)
				previousChord = False
				lilyList.append('\t\t\t}\n')
				if textUnderLineNames != None:
					for textUnderLine in textUnderLineNames:
						lilyList.append('\t\t\t\\addlyrics { ' + ' '.join(textUnderLineDict.get(textUnderLine, '')) + ' }\n')
				textUnderLineDict = {}
				textUnderLineStrings = {}
				textUnderLineNames = None

				if barGraphLineNames != None:
					for barGraphLine in barGraphLineNames:
						lilyList.append('\t\t\t\\addlyrics { ' + ' '.join(barGraphLineDict[barGraphLine]) + ' }\n')
				barGraphLineDict = {}
				barGraphLineNames = None

				if lineGraphLineNames != None:
					for lineGraphLine in lineGraphLineNames:
						lilyList.append('\t\t\t\\addlyrics { ' + ' '.join(lineGraphLineDict[lineGraphLine]) + ' }\n')
				lineGraphLineDict = {}
				lineGraphLineNames = None

			#reset parameters to force them to be re-evaluated
			keysig = None
			clef = None
			time = None
			lilyList.append('>> \n')
		lilyList.append('\t>> }\n')
	lilyList.append('}\n')
	return ''.join(lilyList)

