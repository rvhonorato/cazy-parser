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
# create a parsed database using CAZY html structure
import os
import progressbar
import re
import string
import sys
import time
import urllib
from bs4 import BeautifulSoup
# ==============================================================================#

checkpoint_f = 'cp.chk'
fam_checkpoint_f = 'fam.chk'


def init_bar():
    """ Initilize progress bar """
    bar = progressbar.ProgressBar(widgets=[
        ' ',
        progressbar.Timer(),
        ' ',
        progressbar.Percentage(),
        ' ',
        progressbar.Bar('█', '[', ']'),
        ' ',
        progressbar.ETA(), ' '
    ]
    )
    return bar


def fetch_species():
    """ Gather species names and IDs (full genome only) """
    print('> Gathering species with full genomes')
    # a = archea // b = bacteria // e = eukaryota // v = virus
    species_domain_list = ['a', 'b', 'e', 'v']
    species_dic = {}

    bar = init_bar()
    bar.max_value = len(string.ascii_uppercase) * len(species_domain_list)
    bar.start()

    counter = 0
    for domain in species_domain_list:
        for initial in string.ascii_uppercase:
            counter += 1
            bar.update(counter)
            link = 'http://www.cazy.org/%s%s.html' % (domain, initial)
            f = urllib.request.urlopen(link)
            species_list_hp = f.read().decode("utf-8")
            # parse webpage
            index_list = re.findall(
                '"http://www.cazy.org/{}(\d.*).html" class="nav">(.*)</a>'.format(species_domain_list), species_list_hp)
            for entry in index_list:
                index, species = entry
                try:
                    species_dic[species].append(index)
                except KeyError:
                    species_dic[species] = [index]
    bar.finish()

    # Double check to see which of the species codes are valid
    for j, species in enumerate(species_dic.keys()):
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

    return species_dic


def fetch_families(main_link):
    """ Identify family link structure and return a list """
    soup = BeautifulSoup(urllib.request.urlopen(main_link), features="html.parser")
    family_table = soup.findAll(name='table')[0]
    rows = family_table.findAll(name='td')
    family_list = [str(r.find('a')['href'].split('/')[-1].split('.html')[0]) for r in rows]

    return family_list


def fetch_links(enzyme_class):
    """ Fetch link structure for an enzyme class """

    # Links need to be fetched everytime since there is no way (?) to guarantee
    #  that all were previously fetched without actually fetching them.
    main_class_link = 'http://www.cazy.org/%s.html' % enzyme_class

    family_list = fetch_families(main_class_link)

    bar = init_bar()
    bar.max_value = len(family_list)
    bar.start()

    page_list = []
    for j, family in enumerate(family_list):
        bar.update(j + 1)
        main_link = 'http://www.cazy.org/%s.html' % family

        # TODO: Implement checkpoint for link fetching

        family_soup = BeautifulSoup(urllib.request.urlopen(main_link), features="html.parser")
        superfamily_list = [l.find('a')['href'] for l in family_soup.findAll('span', attrs={'class': 'choix'})][1:]

        superfamily_list = [f for f in superfamily_list if 'structure' not in f]  # remove structure tab for parsing
        for main_link in superfamily_list:
            page_zero = main_link
            soup = BeautifulSoup(urllib.request.urlopen(main_link), features="html.parser")

            # Get page list for the family
            page_index_list = soup.findAll(name='a', attrs={'class': 'lien_pagination'})
            if bool(page_index_list):

                # =====================#
                # be careful with this #
                first_page_idx = int(re.findall('=(\d*)#', str(page_index_list[0]))[0])
                last_page_idx = int(re.findall('=(\d*)#', str(page_index_list[-2]))[0])
                # =====================#

                page_list.append(page_zero)
                for i in range(first_page_idx, last_page_idx + first_page_idx, first_page_idx):
                    link = 'http://www.cazy.org/' + page_index_list[0]['href'].split('=')[0] + '=' + str(i)
                    page_list.append(link)

            else:
                page_list.append(page_zero)

    return page_list


def check_status(chk_f, link):
    """ Check if contents of this link have been downloaded """

    if os.path.isfile(chk_f):
        for l in open(chk_f):
            if link in l:
                return True


def save_status(chk_f, link):
    """ Save link address in checkpoint file """
    open(chk_f, 'a').write('{}\n'.format(link))


def fetch_data(link_list, species_dic, out_f):
    """ Parse list of links and extract information """

    bar = init_bar()
    bar.max_value = len(link_list)
    bar.start()

    protein_counter = 0
    for j, link in enumerate(link_list):

        db_dic = {}
        bar.update(j + 1)

        if check_status(checkpoint_f, link):
            continue

        # tr  = rows // # td = cells
        soup = BeautifulSoup(urllib.request.urlopen(link), features="html.parser")
        table = soup.find('table', attrs={'class': 'listing'})
        domain = ''
        family = link.split('.org/')[-1].split('_')[0]

        # consistency check to look for deleted families. i.e. GH21
        try:
            table.findAll('tr')
        except AttributeError:
            # not a valid link, move on
            continue
        for row in table.findAll('tr'):
            try:
                if row['class'] == 'royaume' and row.text != 'Top':
                    domain = str(row.text).lower()
            except KeyError:
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
                    db_dic[protein_counter]['genbank'] = tds[3].find('a').text.replace('&nbsp;', '')  # get latest entry
                except KeyError:
                    # there is a crazy aberration when there is no genbank available
                    db_dic[protein_counter]['genbank'] = 'unavailable'

                db_dic[protein_counter]['uniprot'] = tds[4].text.replace('&nbsp;', '')
                db_dic[protein_counter]['pdb'] = tds[5].text.replace('&nbsp;', '')

                # check if this is species has a complete genome
                try:
                    db_dic[protein_counter]['organism_code'] = species_dic[tds[2].text.replace('&nbsp;', '')]
                except KeyError:
                    db_dic[protein_counter]['organism_code'] = 'invalid'

                # check if there are subfamilies
                try:
                    db_dic[protein_counter]['subfamily'] = tds[6].text.replace('&nbsp;', '')
                except KeyError:
                    db_dic[protein_counter]['subfamily'] = ''

                # if 'characterized' in main_link:
                if 'characterized' in link:
                    db_dic[protein_counter]['tag'] = 'characterized'
                else:
                    db_dic[protein_counter]['tag'] = ''

                protein_counter += 1

        save_output(out_f, db_dic)
        save_status(checkpoint_f, link)

    bar.finish()


def save_output(output_f, d_dic):
    """ Save information as .csv file """
    if not os.path.isfile(output_f):
        out = open(output_f, 'w')
        header = ','.join(d_dic[0].keys()) + '\n'
        out.write(header)
    else:
        out = open(output_f, 'a')

    for p in d_dic:
        tbw = ','.join(list(d_dic[p].values())).replace('\n', '')
        tbw += "\n"
        out.write(tbw)
    out.close()


def clean(out_f):
    """ Remove duplicates from output file """
    file_l = open(out_f).readlines()
    new_file_l = list(set(file_l))
    open(out_f, 'w').write(''.join(new_file_l))
    del file_l
    del new_file_l


def logo():
    version = '1.4'
    print('')
    print('┌─┐┌─┐┌─┐┬ ┬   ┌─┐┌─┐┬─┐┌─┐┌─┐┬─┐')
    print('│  ├─┤┌─┘└┬┘───├─┘├─┤├┬┘└─┐├┤ ├┬┘')
    print('└─┘┴ ┴└─┘ ┴    ┴  ┴ ┴┴└─└─┘└─┘┴└─ v{}'.format(version))
    print('')
    print('This is the database creator script')
    print('')
    print('(get a coffee, this will take a while)')
    print('')


def main():

    logo()

    species_dic = fetch_species()

    enzyme_list = [
        'Glycoside-Hydrolases',
        'GlycosylTransferases',
        'Polysaccharide-Lyases',
        'Carbohydrate-Esterases',
        'Auxiliary-Activities'
    ]

    for enzyme_name in enzyme_list:
        print('>> {}'.format(enzyme_name))
        output_f = 'CAZy_DB_{}_{}.csv'.format(enzyme_name, time.strftime("%d-%m-%Y"))

        print('> Fetching links')
        page_list = fetch_links(enzyme_name)

        print('> Gathering data')
        fetch_data(page_list, species_dic, output_f)

        clean(output_f)

    sys.exit(0)


if __name__ == '__main__':
    main()
