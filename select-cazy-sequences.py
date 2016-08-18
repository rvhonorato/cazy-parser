#!/usr/bin/env python
#==============================================================================#
# Copyright (C) 2016  Rodrigo Honorato
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#==============================================================================#

## Select a group of protein sequences from the CAZY db
#
# This script need a CAZY_DB_xx-xx-xxxx.csv
#==============================================================================#
# Modules
import os, sys, itertools, urllib, argparse
#==============================================================================#

#==============================================================================#
# Functions
#==============================================================================#
def fetch_ncbi_seq(protein_id):
	if protein_id == 'unavailable':
		# there is no id for this...!
		fasta = ''
		check = True
	else:
		link = 'http://www.ncbi.nlm.nih.gov/sviewer/viewer.cgi?tool=portal&sendto=on&log$=seqview&db=protein&dopt=fasta&sort=&val=%s&from=begin&to=end&maxplex=1' % protein_id
		check = False
		while check == False:
			try:
				fasta = urllib.urlopen(link).read()
				if fasta[0] != '>':
					# not a true fasta line
					pass
				if fasta[0] == '>':
					# this is it!
					check = True
			except:
				pass
	return fasta

#==============================================================================#
# Options
#==============================================================================#
parser = argparse.ArgumentParser(description='CAZY-Parser, a simple way to retrieve fasta sequences from CAZY DB')

parser.add_argument('--db', action = "store", dest = 'db_file',
	help = 'Database file')

parser.add_argument('--family', action = "store", dest = 'target_family',
	help = 'Family to be searched')

parser.add_argument('--subfamily', action = "store_true", default = False,
	help = 'Create a multifasta for each subfamily, DEFAULT: FALSE')

parser.add_argument('--characterized', action = "store_true", default = False,
	help = 'Create a multifasta containing only characterized enzymes, DEFAULT: FALSE')

results = parser.parse_args()

#==============================================================================#
# Input
#==============================================================================#
db_f = open(results.db_file).readlines()
header = db_f[0].split('\t')

db = {}
for i, l in enumerate(db_f[1:]):
	db[i] = {}
	data = l.split('\t')
	# init dictionary
	for c, idx in enumerate(header):
		try:
			db[i][idx] = data[c]
		except IndexError:
			db[i][idx] = ''

#==============================================================================#
# Select all family
#==============================================================================#
if bool(results.target_family):

	selection_list = []
	for e in db:
		if db[e]['family'] == results.target_family:
			selection_list.append(db[e]['genbank'])

	# output
	print '>> Selecting all %i proteins from Family %s' % (len(selection_list), results.target_family)
	out_f = '%s.fasta' % results.target_family
	out = open(out_f, 'w')
	for i, protein in enumerate(selection_list):
		print '> %s :: %i' % (protein, len(selection_list)-i)
		fasta = fetch_ncbi_seq(protein)
		out.write(fasta)

	out.close()

#==============================================================================#
# Select by subfamily
#==============================================================================#

if bool(results.subfamily):

	selection_dic = {}
	for e in db:
		if db[e]['family'] == results.target_family and bool(db[e]['subfamily']):
			try:
				selection_dic[db[e]['subfamily']].append(db[e]['genbank'])
			except:
				selection_dic[db[e]['subfamily']] = [db[e]['genbank']]

	# output
	print '>> Creating multifasta for all %i subfamilies for Family %s' % (len(selection_dic), results.target_family)
	for sub in selection_dic:
		out_f = '%s_sub%s.fasta' % (results.target_family, sub)
		out = open(out_f,'w')

		for i, protein in enumerate(selection_dic[sub]):
			print '> sub%s :: %s :: %i' % (sub, protein, len(selection_dic[sub])-i)
			fasta = fetch_ncbi_seq(protein)
			out.write(fasta)

		out.close()

#==============================================================================#
# Select by characterization
#==============================================================================#

if bool(results.characterized):

	selection_list = []
	for e in db:
		if db[e]['family'] == results.target_family and bool(db[e]['tag']):
			selection_list.append(db[e]['genbank'])

	# output
	print '>> Selecting %i CHARACTERIZED proteins for Family %s' % (len(selection_list), results.target_family)
	out_f = '%s_characterized.fasta' % results.target_family
	out = open(out_f, 'w')
	for i, protein in enumerate(selection_list):
		print '> %s :: %i' % (protein, len(selection_list)-i)
		fasta = fetch_ncbi_seq(protein)
		out.write(fasta)

	out.close()
