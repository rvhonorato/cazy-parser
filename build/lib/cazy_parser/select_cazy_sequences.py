#!/usr/bin/env python
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

# Select a group of protein sequences from the CAZY db
#
# This script need a CAZY_DB_xx-xx-xxxx.csv
# ==============================================================================#
# Modules
import argparse

# ==============================================================================#

# ==============================================================================#
# Options
# ==============================================================================#
parser = argparse.ArgumentParser(description='CAZY-Parser, a simple way to retrieve fasta sequences from CAZY DB')

parser.add_argument('--db', action="store", dest='db_file', help='Database file')

parser.add_argument('--family', action="store", dest='target_family', help='Family to be searched')

parser.add_argument('--subfamily', action="store_true", default=False, help='Create a multifasta for each subfamily, DEFAULT: FALSE')

parser.add_argument('--characterized', action="store_true", default=False, help='Create a multifasta containing only characterized enzymes, DEFAULT: FALSE')

results = parser.parse_args()

# ==============================================================================#
# Input
# ==============================================================================#
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

# ==============================================================================#
# Select all family
# ==============================================================================#
if bool(results.target_family):

    selection_list = []
    for e in db:
        if db[e]['family'] == results.target_family:
            selection_list.append(db[e]['genbank'])

    print '>> Selecting all %i proteins from Family %s' % (len(selection_list), results.target_family)

    l = list(set(selection_list))

    out_f = '%s.csv' % results.target_family
    out = open(out_f, 'w')
    out.write('\n'.join(l))
    out.close()

# ==============================================================================#
# Select by subfamily
# ==============================================================================#

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
        l = list(set(selection_dic[sub]))

        out_f = '%s_sub%s.csv' % (results.target_family, sub)
        out = open(out_f, 'w')
        out.write('\n'.join(l))
        out.close()

# ==============================================================================#
# Select by characterization
# ==============================================================================#

if bool(results.characterized):

    selection_list = []
    for e in db:
        if db[e]['family'] == results.target_family and bool(db[e]['tag']):
            selection_list.append(db[e]['genbank'])

    print '>> Selecting %i CHARACTERIZED proteins for Family %s' % (len(selection_list), results.target_family)

    l = list(set(selection_list))

    out_f = '%s_characterized.csv' % results.target_family
    out = open(out_f, 'w')
    out.write('\n'.join(selection_list))
    out.close()
