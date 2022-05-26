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

import argparse
import sys


def logo():
    version = "1.4.2"
    print("")
    print("┌─┐┌─┐┌─┐┬ ┬   ┌─┐┌─┐┬─┐┌─┐┌─┐┬─┐")
    print("│  ├─┤┌─┘└┬┘───├─┘├─┤├┬┘└─┐├┤ ├┬┘")
    print("└─┘┴ ┴└─┘ ┴    ┴  ┴ ┴┴└─└─┘└─┘┴└─ v{}".format(version))
    print("")
    print("This is the accession code retrieval script")
    print("")


def load_db(f):
    db_f = open(f).readlines()
    sep = ","
    header = db_f[0].split(sep)

    print(">> Loading {}".format(f))
    db = {}
    for i, l in enumerate(db_f[1:]):
        db[i] = {}
        data = l.split(sep)
        # init dictionary
        for c, idx in enumerate(header):
            try:
                db[i][idx] = data[c]
            except IndexError:
                db[i][idx] = ""
    return db


def select_fam(fam, db):
    selection_list = []
    for e in db:
        if db[e]["family"] == fam:
            selection_list.append(db[e]["genbank"])

    print(
        ">> Retrieving all {} accession codes for Family {}".format(
            len(selection_list), fam
        )
    )

    sele_l = list(set(selection_list))
    out_f = "%s.csv" % fam
    print(">> Creating {}".format(out_f))
    out = open(out_f, "w")
    out.write("\n".join(sele_l))
    out.close()


def select_subfam(fam, db):
    selection_dic = {}
    for e in db:
        if db[e]["family"] == fam and bool(db[e]["subfamily"]):
            try:
                selection_dic[db[e]["subfamily"]].append(db[e]["genbank"])
            except KeyError:
                selection_dic[db[e]["subfamily"]] = [db[e]["genbank"]]

    # output
    print(
        ">> Retrieving accession codes for {} subfamilies for Family {}".format(
            len(selection_dic), fam
        )
    )
    for sub in selection_dic:
        s_l = list(set(selection_dic[sub]))
        out_f = "{}_sub{}.csv".format(fam, sub)
        print(">> Creating {}".format(out_f))
        out = open(out_f, "w")
        out.write("\n".join(s_l))
        out.close()


def select_char(fam, db):
    selection_list = []
    for e in db:
        if db[e]["family"] == fam and bool(db[e]["tag"]):
            selection_list.append(db[e]["genbank"])

    print(
        ">> Selecting {} CHARACTERIZED proteins for Family {}".format(
            len(selection_list), fam
        )
    )

    out_f = "{}_characterized.csv".format(fam)
    out = open(out_f, "w")
    print(">> Creating {}".format(out_f))
    out.write("\n".join(selection_list))
    out.close()


def main():
    logo()

    parser = argparse.ArgumentParser(
        description="Select accession codes for a given protein family. Optional: Select subfamilies and/or "
        "characterized enzymes"
    )

    parser.add_argument(
        "--db",
        action="store",
        dest="db_file",
        help="Database file generated by cazy-parser",
    )

    parser.add_argument(
        "--family",
        action="store",
        dest="target_family",
        help="Family to be searched ex. GH5",
    )

    parser.add_argument(
        "--subfamily",
        action="store_true",
        default=False,
        help="(Optional) Create a file with accession codes for each subfamily",
    )

    parser.add_argument(
        "--characterized",
        action="store_true",
        default=False,
        help="(Optional) Create a file with accession codes only for characterized enzymes",
    )

    results = parser.parse_args()

    check = False
    if results.db_file is None:
        print("\n>> [ERROR] Missing database file\n")
        check = True

    if results.target_family is None:
        print("\n>> [ERROR] Missing target family\n")
        check = True

    if check:
        parser.print_help()
        sys.exit(0)

    db = load_db(results.db_file)

    if bool(results.target_family):
        select_fam(results.target_family, db)

    if bool(results.subfamily):
        select_subfam(results.target_family, db)

    if bool(results.characterized):
        select_char(results.target_family, db)

    sys.exit(0)


if __name__ == "__main__":
    main()
