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

#==============================================================================#
# create a parsed database exploting CAZY html structure
import os, sys, urllib, re, string, time, string
from BeautifulSoup import BeautifulSoup

#==============================================================================#
# Species part
#==============================================================================#
print '>> Gathering species codes for species with full genomes'
# a = archea // b = bacteria // e = eukaryota // v = virus
species_domain_list = ['a', 'b', 'e', 'v']
species_dic = {}
for initial in string.uppercase:
	for domain in species_domain_list:
		link = 'http://www.cazy.org/%s%s.html' % (domain, initial)
		f = urllib.urlopen(link)
		species_list_hp = f.read()
		# parse webpage
		index_list = re.findall('"http://www.cazy.org/(b\d.*).html" class="nav">(.*)</a>', species_list_hp)
		for entry in index_list:
			index, species = entry
			try:
				species_dic[species].append(index)
			except:
				species_dic[species] = [index]

# Double check to see which of the species codes are valid
for species in species_dic:
	entry_list = species_dic[species]
	if len(entry_list) > 1:
		# More than one entry for this species
		#  > This is (likely) a duplicate
		#  > Use the higher number, should be the newer page
		newer_entry = max([int(i.split('b')[-1]) for i in entry_list])
		selected_entry = 'b%i' % newer_entry

		species_dic[species] = selected_entry
	else:
		species_dic[species] = species_dic[species][0]

#==============================================================================#
# Enzyme class part
#==============================================================================#

enzyme_classes = ['Glycoside-Hydrolases',
	'GlycosylTransferases',
	'Polysaccharide-Lyases',
	'Carbohydrate-Esterases',
	'Auxiliary-Activities']

db_dic = {}
protein_counter = 0
for e_class in enzyme_classes:
	print '>> %s' % e_class
	main_class_link = 'http://www.cazy.org/%s.html' % e_class

	#==============================================================================#
	# Family section
	#==============================================================================#
	soup = BeautifulSoup(urllib.urlopen(main_class_link))
	family_table = soup.findAll(name='table')[0]
	rows = family_table.findAll(name='td')

	family_list = [str(r.find('a')['href'].split('/')[-1].split('.html')[0]) for r in rows]

	print '>> %i families found on %s' % (len(family_list), main_class_link)
	#==============================================================================#
	# Identification section
	#==============================================================================#
	for family in family_list:
		print '> %s' % family
		#
		main_link = 'http://www.cazy.org/%s.html' % family
		family_soup = BeautifulSoup(urllib.urlopen(main_link))
		# main_link_dic = {'http://www.cazy.org/%s_all.html#pagination_PRINC' % family: '',
		# 	'http://www.cazy.org/%s_characterized.html#pagination_PRINC' % family: 'characterized'}
		#====================#
		superfamily_list = [l.find('a')['href'] for l in family_soup.findAll('span', attrs={'class':'choix'})][1:]

		# remove structure tab, for now
		superfamily_list = [f for f in superfamily_list if not 'structure' in f]

		# DEBUG
		# superfamily_list = superfamily_list[:-2]
		#====================#
		for main_link in superfamily_list:

			page_zero = main_link

			soup = BeautifulSoup(urllib.urlopen(main_link))

			# Get page list for the family // 1, 2, 3, 4, 5, 7
			page_index_list = soup.findAll(name = 'a', attrs={'class':'lien_pagination'})
			# page_list = ['http://www.cazy.org/' + str(l['href']) for l in page_index_list] # deprecated
			if bool(page_index_list):
				first_page_idx = int(page_index_list[0]['href'].split('PRINC=')[-1].split('#')[0]) # be careful with this
				last_page_idx = int(page_index_list[-2]['href'].split('PRINC=')[-1].split('#')[0]) # be careful with this

				# generate page_list
				page_list = []
				page_list.append(page_zero)
				for i in range(first_page_idx, last_page_idx+first_page_idx, first_page_idx):
					link = 'http://www.cazy.org/' + page_index_list[0]['href'].split('=')[0] + '=' + str(i) + '#' + page_index_list[0]['href'].split('#')[1]
					page_list.append(link)
			else:
				page_list = [page_zero]

			# page_list.append(main_link) # deprecated
			# page_list = list(set(page_list)) # deprecated
			for link in page_list:
				# print link
				# tr  = rows // # td = cells
				soup = BeautifulSoup(urllib.urlopen(link))
				table = soup.find('table', attrs={'class':'listing'})
				domain = ''

				# consistency check to look for deleted families. i.e. GH21
				try:
					check = table.findAll('tr')
				except AttributeError:
					# not a valid link, move on
					continue

				for row in table.findAll('tr'):
					try:
						if row['class'] == 'royaume' and row.text != 'Top':
							domain = str(row.text).lower()
					except:
						pass

					tds = row.findAll('td')
					if len(tds) > 1 and tds[0].text != 'Protein Name':
						# valid line
						db_dic[protein_counter] = {}

						db_dic[protein_counter]['protein_name'] = tds[0].text.replace('&nbsp;','')
						db_dic[protein_counter]['family'] = family
						db_dic[protein_counter]['domain'] = domain
						db_dic[protein_counter]['ec'] = tds[1].text.replace('&nbsp;','')
						db_dic[protein_counter]['organism'] = tds[2].text.replace('&nbsp;','')
						try:
							db_dic[protein_counter]['genbank'] = tds[3].find('a').text.replace('&nbsp;','') # get latest entry
						except:
							# there is a crazy aberration when there is no genbank available
							db_dic[protein_counter]['genbank'] = 'unavailable'
						#
						db_dic[protein_counter]['uniprot'] = tds[4].text.replace('&nbsp;','')
						db_dic[protein_counter]['pdb'] = tds[5].text.replace('&nbsp;','')

						# check if this is species has a complete genome
						try:
							db_dic[protein_counter]['organism_code'] = species_dic[tds[2].text.replace('&nbsp;','')]
						except:
							db_dic[protein_counter]['organism_code'] = 'invalid'

						# check if there are subfamilies
						try:
							db_dic[protein_counter]['subfamily'] = tds[6].text.replace('&nbsp;','')
							print tds[6].text.replace('&nbsp;','')
						except:
							db_dic[protein_counter]['subfamily'] = ''

						if 'characterized' in main_link:
							db_dic[protein_counter]['tag'] = 'characterized'
						else:
							db_dic[protein_counter]['tag'] = ''
						# debug entries
						# print '\t'.join(db_dic[protein_counter].keys())
						# print '\t'.join(db_dic[protein_counter].values())
						protein_counter += 1

#==============================================================================#
# Remove duplicates #
#
#  Note: since there are no unique identifiers, there's no other way to do this,
# we must compare each entry with the whole list (right?).
#
#==============================================================================#
exit()
repeated_counter = 0
blacklist = []
for a in db_dic:
	a_check = False
	a_list = db_dic[a].values()
	del a_list[3]
	a_str = '\t'.join(a_list)
	for b in db_dic:
		b_check = False
		b_list = db_dic[b].values()
		del b_list[3]
		b_str = '\t'.join(b_list)
		if a_str == b_str and a != b:
			#
			if db_dic[a]['tag'] == 'characterized':
				a_check = True
			#
			if db_dic[b]['tag'] == 'characterized':
				b_check = True
			#
			if a_check == True and b_check == False:
				# keep a
				blacklist.append(b)
			#
			if a_check == False and b_check == True:
				# keep b
				blacklist.append(a)
			#
			if a_check == True and b_check == True:
				# repeated characterized entry, do nothing
				# keep A
				repeated_counter += 1
				blacklist.append(b)
				# print 'C', '#' * 10
				# print a_str
				# print b_str
				# print '#' * 10
				# pass
			#
			if a_check == False and b_check == False:
				# repeated uncharacterized entry, do nothing
				# keep A
				repeated_counter += 1
				blacklist.append(b)
				# print 'NC','#' * 10
				# print a_str
				# print b_str
				# print '#' * 10

				# pass

print repeated_counter, 'repeated entries!'

# Remove blacklisted keys
blacklist = list(set(blacklist))
for k in blacklist:
	del db_dic[k]

# Ouput
output_f = 'CAZy_DB_%s.csv' % time.strftime("%d-%m-%Y")
out = open(output_f, 'w')
header = '\t'.join(db_dic[0].keys())
out.write(header + '\n')

for p in db_dic:
	# print p, '\t'.join(db_dic[p].values())
	tbw = '\t'.join(db_dic[p].values())
	tbw = tbw.encode('utf8') # make sure codification is ok
	out.write(tbw + '\n')

out.close()

# done.
