#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==============================================================================#
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
# ==============================================================================#

# ==============================================================================#
# create a parsed database exploting CAZY html structure
import argparse
import progressbar
import re
import string
import sys
import time
import urllib

from bs4 import BeautifulSoup


def main():
    global family
    print ('\n'
           '\n'
           '	┌─┐┌─┐┌─┐┬ ┬   ┌─┐┌─┐┬─┐┌─┐┌─┐┬─┐\n'
           '	│  ├─┤┌─┘└┬┘───├─┘├─┤├┬┘└─┐├┤ ├┬┘\n'
           '	└─┘┴ ┴└─┘ ┴    ┴  ┴ ┴┴└─└─┘└─┘┴└─ v1.3\n'
           '\n'
           '	This is the database creator script\n'
           '\n'
           '	')


    parser = argparse.ArgumentParser(
        description='Generate a comma separated table with information gathered from the CAZy database; internet connection is required.')
    args = parser.parse_args()

    bar = progressbar.ProgressBar(
        widgets=[' ', progressbar.Timer(), ' ', progressbar.Percentage(), ' ', progressbar.Bar('█', '[', ']'), ' ',
                 progressbar.ETA(), ' '])

    # ==============================================================================#
    # Species part
    # ==============================================================================#
    print '> Gathering species with full genomes'
    # a = archea // b = bacteria // e = eukaryote // v = virus
    species_domain_list = ['a', 'b', 'e', 'v']
    species_dic = {}

    bar.max_value = len(string.uppercase) * len(species_domain_list)
    bar.start()

    counter = 0
    for initial in string.uppercase:
        for domain in species_domain_list:
            counter += 1
            bar.update(counter)
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
    bar.finish()

    # Double check to see which of the species codes are valid
    print '\n> Checking'

    bar.max_value = len(species_dic.keys())
    bar.start()
    for j, species in enumerate(bar(species_dic.keys())):
        bar.update(j + 1)
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
    bar.finish()

    # ==============================================================================#
    # Enzyme class part
    # ==============================================================================#

    print '\n\n> Extracting information from classes (get a coffee, this will take a while)'

    enzyme_classes = ['Glycoside-Hydrolases',
                      'GlycosylTransferases',
                      'Polysaccharide-Lyases',
                      'Carbohydrate-Esterases',
                      'Auxiliary-Activities']

    db_dic = {}
    protein_counter = 0
    family_counter = 0
    for e_class in enzyme_classes:
        main_class_link = 'http://www.cazy.org/%s.html' % e_class

        # ==============================================================================#
        # Family section
        # ==============================================================================#
        soup = BeautifulSoup(urllib.urlopen(main_class_link), features='html.parser')
        family_table = soup.findAll(name='table')[0]
        rows = family_table.findAll(name='td')

        family_list = [str(r.find('a')['href'].split('/')[-1].split('.html')[0]) for r in rows]

        print '\n>> %s - fetching families' % e_class
        # ==============================================================================#
        # Identification section
        # ==============================================================================#
        page_list = []

        #### WIP
        # if os.path.isfile('%s.link' % e_class):
        # 	family_check = dict([(f, False) for f in family_list])
        # 	print '>> Looking for .link file [experimental]'
        # 	for l in open('%s.link' % e_class):
        # 		page_list.append(l)
        # 		# improve this
        # 		for f in family_check:
        # 			if f in l:
        # 				family_check[f] = True
        # 	for f in family_check:
        # 		if family_check[f] == False:
        # 			print '>>> %s.link looks incomplete, delete and try again' % e_class
        # 			exit()
        # else:
        ###########

        # fetch
        bar.max_value = len(family_list)
        bar.start()

        out = open('%s.link' % e_class, 'w')
        for j, family in enumerate(family_list):
            bar.update(j + 1)
            # print '\n>>> %s' % family
            main_link = 'http://www.cazy.org/%s.html' % family
            family_soup = BeautifulSoup(urllib.urlopen(main_link), features='html.parser')
            # main_link_dic = {'http://www.cazy.org/%s_all.html#pagination_PRINC' % family: '',
            # 	'http://www.cazy.org/%s_characterized.html#pagination_PRINC' % family: 'characterized'}
            # ====================#
            superfamily_list = [l.find('a')['href'] for l in family_soup.findAll('span', attrs={'class': 'choix'})][1:]

            # remove structure tab, for now
            superfamily_list = [f for f in superfamily_list if not 'structure' in f]

            # ====================#
            for main_link in superfamily_list:

                page_zero = main_link

                soup = BeautifulSoup(urllib.urlopen(main_link), features='html.parser')

                # Get page list for the family // 1, 2, 3, 4, 5, 7
                page_index_list = soup.findAll(name='a', attrs={'class': 'lien_pagination'})

                if bool(page_index_list):

                    first_page_idx = int(re.findall('=(\d*)#', str(page_index_list[0]))[0])  # be careful with this
                    last_page_idx = int(re.findall('=(\d*)#', str(page_index_list[-2]))[0])  # be careful with this

                    page_list.append(page_zero)
                    out.write('%s\n' % page_zero)

                    for i in range(first_page_idx, last_page_idx + first_page_idx, first_page_idx):
                        link = 'http://www.cazy.org/' + page_index_list[0]['href'].split('=')[0] + '=' + str(i)
                        page_list.append(link)
                        out.write('%s\n' % link)
                else:
                    page_list.append(page_zero)
                    out.write('%s\n' % page_zero)

        out.close()

        print '\n>>> Downloading'

        bar.max_value = len(page_list)
        bar.start()
        for j, link in enumerate(page_list):
            bar.update(j + 1)
            # tr  = rows // # td = cells
            soup = BeautifulSoup(urllib.urlopen(link), features='html.parser')
            table = soup.find('table', attrs={'class': 'listing'})
            domain = ''
            family = link.split('.org/')[-1].split('_')[0]
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
                    db_dic[protein_counter]['protein_name'] = tds[0].text.replace('&nbsp;', '')
                    db_dic[protein_counter]['family'] = family
                    db_dic[protein_counter]['domain'] = domain
                    db_dic[protein_counter]['ec'] = tds[1].text.replace('&nbsp;', '')
                    db_dic[protein_counter]['organism'] = tds[2].text.replace('&nbsp;', '')
                    try:
                        db_dic[protein_counter]['genbank'] = tds[3].find('a').text.replace('&nbsp;',
                                                                                           '')  # get latest entry
                    except:
                        # there is a crazy aberration when there is no genbank available
                        db_dic[protein_counter]['genbank'] = 'unavailable'

                    db_dic[protein_counter]['uniprot'] = tds[4].text.replace('&nbsp;', '')
                    db_dic[protein_counter]['pdb'] = tds[5].text.replace('&nbsp;', '')
                    # check if this is species has a complete genome
                    try:
                        db_dic[protein_counter]['organism_code'] = species_dic[tds[2].text.replace('&nbsp;', '')]
                    except:
                        db_dic[protein_counter]['organism_code'] = 'invalid'
                    # check if there are subfamilies
                    try:
                        db_dic[protein_counter]['subfamily'] = tds[6].text.replace('&nbsp;', '')
                    except:
                        db_dic[protein_counter]['subfamily'] = ''
                    # if 'characterized' in main_link:
                    if 'characterized' in link:
                        db_dic[protein_counter]['tag'] = 'characterized'
                    else:
                        db_dic[protein_counter]['tag'] = ''
                    # debug entries
                    # print '\t'.join(db_dic[protein_counter].keys())
                    # print '\t'.join(db_dic[protein_counter].values())
                    protein_counter += 1
                    family_counter += 1
        bar.finish()

        print '> %i entries found for %s' % (family_counter, family)

    # Ouput
    output_f = 'CAZy_DB_%s.csv' % time.strftime("%d-%m-%Y")
    out = open(output_f, 'w')
    header = '\t'.join(db_dic[0].keys())
    out.write(header + '\n')

    for p in db_dic:
        tbw = '\t'.join(db_dic[p].values())
        tbw = tbw.encode('utf8')  # make sure codification is ok
        out.write(tbw + '\n')

    out.close()

    sys.exit(0)


if __name__ == '__main__':
    main()

# done.
