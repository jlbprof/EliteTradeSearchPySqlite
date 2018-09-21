#!/usr/bin/python

# Author: Julian Brown
# Original Date: Sept 04, 2018
# License: MIT License, a copy of the license is in this repo
#

import sys
import getopt
import urllib
import sqlite3
import os
import json
import csv

#
# EliteTradeSearchPySqlite
#
# This is a set of scripts that contain information that helps playing the
# game Elite Dangerous.
#
# EliteTradeSearchPySqlite/updatedb.py
#
# This is one script of hopefully many that allow you to download the latest
# information from the Eddb.io site about the commodities, star systems, space
# stations, and commodity prices at those stations.   This script will
# download those files and insert them into a SQLite database for easy
# perusal.  The data gets old quickly, use this script to keep the database
# relevant for searching.
#
# Note: this should always be run in the EliteTradeSearchPySqlite directory as
# all of its's sister scripts and files will be located here.  This file may
# contain upwards of 20 gigs during operations.
#
# The files and format that this script downloads and inserts into the
# SQLiteDB.
#
# https://eddb.io/archive/v5/commodities.json
#
# This file is in JSON format and here are just a few lines from a typical
# download.
# [
#   {
#      "ed_id" : 128672162,
#      "is_rare" : 0,
#      "min_sell_price" : 1298,
#      "sell_price_upper_average" : 13368,
#      "is_non_marketable" : 0,
#      "max_sell_price" : 15769,
#      "max_buy_price" : null,
#      "min_buy_price" : null,
#      "average_price" : 11912,
#      "id" : 334,
#      "category_id" : 16,
#      "buy_price_lower_average" : 0,
#      "category" : {
#         "name" : "Salvage",
#         "id" : 16
#      },
#      "name" : "Gene Bank"
#   },
#
#   From the commodities file we are mostly interested in just the name and
#   id, the id is used as a foreign key in the db.
#
# https://eddb.io/archive/v5/systems_populated.jsonl
#
#    This is a jsonl file, where each line is a complete json object, read
#    each line in one at a time, parse and insert.
#
#{"id":1,"edsm_id":12695,"name":"1 G. Caeli","x":80.90625,"y":-83.53125,"z":-30.8125,"population":6544826,"is_populated":true,"government_id":144,"government":"Patronage","allegiance_id":2,"allegiance":"Empire","state_id":16,"state":"Boom","security_id":32,"security":"Medium","primary_economy_id":4,"primary_economy":"Industrial","power":"Arissa Lavigny-Duval","power_state":"Exploited","power_state_id":32,"needs_permit":false,"updated_at":1536002636,"simbad_ref":"","controlling_minor_faction_id":31816,"controlling_minor_faction":"1 G. Caeli Empire League","reserve_type_id":3,"reserve_type":"Common","minor_faction_presences":[{"minor_faction_id":31816,"state_id":16,"influence":69.1692,"state":"Boom"},{"minor_faction_id":54517,"state_id":80,"influence":3.5035,"state":"None"},{"minor_faction_id":54518,"state_id":80,"influence":1.1011,"state":"None"},{"minor_faction_id":54519,"state_id":80,"influence":6.4064,"state":"None"},{"minor_faction_id":74917,"state_id":80,"influence":5.1051,"state":"None"},{"minor_faction_id":40897,"state_id":80,"influence":11.1111,"state":"None"},{"minor_faction_id":4017,"state_id":80,"influence":3.6036,"state":"None"}]}
#
# https://eddb.io/archive/v5/stations.jsonl
#
#    This is a jsonl file, where each line is a complete json object, read
#    each line in one at a time, parse and insert.
#
#{"id":5,"name":"Reilly Hub","system_id":396,"updated_at":1535563693,"max_landing_pad_size":"L","distance_to_star":171,"government_id":64,"government":"Corporate","allegiance_id":3,"allegiance":"Federation","state_id":80,"state":"None","type_id":8,"type":"Orbis Starport","has_blackmarket":false,"has_market":true,"has_refuel":true,"has_repair":true,"has_rearm":true,"has_outfitting":true,"has_shipyard":true,"has_docking":true,"has_commodities":true,"import_commodities":["Pesticides","Aquaponic Systems","Biowaste"],"export_commodities":["Mineral Oil","Fruit and Vegetables","Grain"],"prohibited_commodities":["Narcotics","Tobacco","Combat Stabilisers","Imperial Slaves","Slaves","Personal Weapons","Battle Weapons","Bootleg Liquor","Landmines"],"economies":["Agriculture"],"shipyard_updated_at":1535909043,"outfitting_updated_at":1535909043,"market_updated_at":1535909042,"is_planetary":false,"selling_ships":["Adder","Eagle Mk. II","Federal Dropship","Hauler","Sidewinder Mk. I","Viper Mk III","Cobra MK IV"],"selling_modules":[738,739,740,743,744,745,748,749,750,753,754,755,758,759,760,793,794,795,796,797,824,826,828,837,838,840,843,851,876,877,878,879,880,882,883,884,886,888,891,892,893,896,897,898,927,928,929,932,933,936,937,938,941,942,946,948,961,962,963,964,966,967,968,998,999,1003,1004,1007,1008,1012,1013,1016,1017,1018,1021,1022,1023,1027,1032,1036,1037,1038,1039,1041,1042,1043,1046,1047,1048,1066,1071,1072,1116,1117,1118,1119,1121,1122,1123,1132,1136,1137,1138,1181,1182,1186,1191,1192,1193,1194,1195,1196,1197,1200,1201,1202,1203,1204,1205,1207,1208,1209,1213,1214,1242,1243,1244,1245,1246,1286,1306,1307,1310,1311,1317,1320,1324,1325,1326,1327,1373,1375,1377,1379,1381,1417,1518,1519,1520,1523,1524,1525,1526,1527,1528,1529,1530,1531,1532,1533,1534,1535,1544,1545,1577,1579,1581,1583,1585,1587,1597,1609,1657],"settlement_size_id":null,"settlement_size":null,"settlement_security_id":null,"settlement_security":null,"body_id":7086578,"controlling_minor_faction_id":13925}
#
# https://eddb.io/archive/v5/listings.csv
#
# This is a CSV file of the price of commodities at all the stations.
#
#id,station_id,commodity_id,supply,supply_bracket,buy_price,sell_price,demand,demand_bracket,collected_at
#1,1,5,0,0,0,744,1185,3,1535999254
#

# put the data into this sqlite db (Note the schema is at the end of this file)
dbfile = 'tradesearch.db'

# information allowing easy use of urllib.urlretrieve
commodities_file = { 'url': "https://eddb.io/archive/v5/commodities.json", 'fname': 'commodities.json' }
systems_file = { 'url': "https://eddb.io/archive/v5/systems_populated.jsonl", 'fname': 'systems_populated.jsonl' }
stations_file = { 'url': "https://eddb.io/archive/v5/stations.jsonl", 'fname': 'stations.jsonl' }
prices_file = { 'url': "https://eddb.io/archive/v5/listings.csv", 'fname': 'prices.csv' }

def usage ():
    print 'updatedb.py -h -c -m -s -t -p -a or --createdb --commodities --systems --stations --prices --all'
    print ' -h - help'
    print ' -c - create database (or re-create it)'
    print ' -m - download and install commodities'
    print ' -s - download and install systems'
    print ' -t - download and install stations'
    print ' -p - download and install prices'
    print ' -a - do all of the above'
    sys.exit (1)

# the status of our sqlite connection
sqlite_access = { 'connected': 0, 'conn': 0 }

# get the connection object from this routine, it uses the above
# status object to maintain the connection

def do_connect ():
    if sqlite_access['connected'] == 1:
        return sqlite_access['conn']
    sqlite_access['conn'] = sqlite3.connect (dbfile)
    sqlite_access['conn'].isolation_level = None
    sqlite_access['connected'] = 1
    return sqlite_access['conn']

# delete the database if it exists
# crate a new db
# inject the schema

def do_createdb ():
    print "Creating db"
    # if file exists, delete it we are creating it from scratch
    if os.access (dbfile, os.F_OK):
        os.remove (dbfile)
    schema = getSchema ()
    conn = do_connect ()
    conn.executescript (schema)
    conn.commit ()
    print "Done"

# download the commodities file
# insert the commodities in the db

def do_commodities ():
    print "Downloading and inserting Commodities"
    urllib.urlretrieve (commodities_file['url'], commodities_file['fname'])
    conn = do_connect ()
    c = conn.cursor ()
    json_fh=open(commodities_file['fname'])
    json_data = json.load(json_fh)
    json_fh.close ()

    try:
        c.execute ("BEGIN")
        c.execute ('DELETE FROM commodities;')
        for index, item in enumerate(json_data):
            id = item["id"]
            name = item["name"]
            print name
            c.execute ('INSERT INTO commodities ("id", "name") VALUES(?, ?);', (id, name))
        c.execute ("COMMIT")
        print "Done"
    except sql.Error:
        print "Failed"
        c.execute ("ROLLBACK")

# download the star systems file
# insert the star systems into the db

def do_systems ():
    print "Downloading and inserting Systems"
    urllib.urlretrieve (systems_file['url'], systems_file['fname'])

    conn = do_connect ()
    c = conn.cursor ()

    # one of the biggest problems with the star system database, is one of the
    # main questions that will be asked.
    #
    # Get me all star systems within 150 light years from this star system.
    # This is both a computationally and a humungous disk space problem.
    #
    # First there is the explosion of distance calculations, basically
    # evertime you ask that question, there are approx 21,000 star systems
    # so I would have to execute the distance calculation 21,000 times.
    # As big a problem that is, it is not the biggest problem.
    #
    # So lets create an db that lists the distances between each star system.
    # That calculation leads to 21,000 squared number of rows which is in
    # excess of 441 million rows.   If there was a table with 3 simple values
    # id1, id2, distance.  Where id1 is the id of star system 1, id2 is the
    # 2nd star system, and distance is the distance between them.   So
    # considering that and having at least one index means that this table
    # alone could be over 31 gb in size, both too expensive to create and
    # to expensive to review.   So we have to do it another way.
    #
    # The new way, is there will be a C program, which is the fastest way
    # to process this calculation, and output a binary 2d array of the
    # 441 million unsigned shorts which will represent the distances.
    # Using an unsigned short means the distance will be between 0 and
    # 65535 light years.   Well rarely will anyone select over 500 ly so
    # that is sufficient and also means that 1 byte would be insufficient
    # (0-255).
    #
    # system_master_list.csv is the list of each index, id, x, y, and z of
    # each system which the C program will use to prepare that array.
    #
    # c program is calc_distance, and creates a file called
    # distance_matrix.bin that is just under 1 gb
    #

    fo = open ("system_master_list.csv", 'w')
    idx = 0

    try:
	# Note, using begin and commit, allows the insertions go much
	# faster
        c.execute ("BEGIN")
        c.execute ('DELETE FROM Systems;')
        f = open (systems_file["fname"], 'r')
        for line_wlf in f:
            line = line_wlf.rstrip('\n')
            json_data = json.loads(line)
            needs_permit = 0
            if json_data["needs_permit"] == "true":
                needs_permit = 1
            print "name :" + json_data["name"]
            mystr = str(idx) + "," + str(json_data["id"]) + "," + str(json_data["x"]) + "," + str(json_data["y"]) + "," + str(json_data["z"]) + "\n"
            fo.write (mystr)
            idx = idx + 1
            c.execute (
                'INSERT INTO Systems ("idx", "id", "edsm_id", "name", "x", "y", "z", "needs_permit") VALUES(?, ?, ?, ?, ?, ?, ?, ?);',
                (idx, json_data["id"], json_data["edsm_id"], json_data["name"], json_data["x"], json_data["y"], json_data["z"], needs_permit))
        c.execute ("COMMIT")
        print "Done"
    except Exception as e:
        print "Failed"
        print e
        c.execute ("ROLLBACK")
        sys.exit (1)

    fo.close ()

    # max_count.txt is the maximum size of the array of systems

    fo = open ("max_count.txt", "w")
    fo.write (str(idx))
    fo.close ()

    # now run the external c program

    print "Calling calc_distances"
    os.system ("./calc_distances");
    print "returned from calc_distances"

# download the stations (where ships can land) file
# insert the stations into the db

def do_stations ():
    print "Downloading and inserting Stations"
    urllib.urlretrieve (stations_file['url'], stations_file['fname'])

    conn = do_connect ()
    c = conn.cursor ()

    try:
        c.execute ("BEGIN")
        c.execute ('DELETE FROM stations;')
        f = open (stations_file["fname"], 'r')
        for line_wlf in f:
            line = line_wlf.rstrip('\n')
            json_data = json.loads(line)
            is_planetary = 0
            if json_data["is_planetary"] == "true":
                is_planetary = 1
            if json_data["distance_to_star"] == None:
                json_data["distance_to_star"] = 100000
            if json_data["max_landing_pad_size"] == None:
                json_data["max_landing_pad_size"] = "S"
            print "name :" + json_data["name"]
            c.execute (
                'INSERT INTO stations ("id", "name", "system_id", "updated_at", "max_landing_pad_size", "distance_to_star", "is_planetary") VALUES(?, ?, ?, ?, ?, ?, ?);',
                (json_data["id"], json_data["name"], json_data["system_id"], json_data["updated_at"], json_data["max_landing_pad_size"], json_data["distance_to_star"], is_planetary))
        c.execute ("COMMIT")
        print "Done"
    except Exception as e:
        print "Failed"
        print e
        c.execute ("ROLLBACK")

# download the prices csv file (note this is a very large file)
# insert them into the db

def do_prices ():
    print "Downloading and inserting Prices"
    urllib.urlretrieve (prices_file['url'], prices_file['fname'])

    conn = do_connect ()
    c = conn.cursor ()

    try:
	# BEGIN and COMMIT are critical, as this would take weeks
	# to insert other wise (up to 4 million rows)
        c.execute ("BEGIN")
        c.execute ('DELETE FROM prices;')
        f = open (prices_file["fname"], 'r')
        csvreader = csv.reader(f, delimiter=',', quotechar='|')
        flag = 1
        count = 0
        for row in csvreader:
            if flag:
                flag = 0
            else:
                c.execute (
                    'INSERT INTO prices ("id", "station_id", "commodity_id", "supply", "buy_price", "sell_price", "demand", "collected_at") VALUES(?, ?, ?, ?, ?, ?, ?, ?);',
                    (row[0], row[1], row[2], row[3], row[5], row[6], row[7], row[9]))
            count = count + 1
            if count % 10000 == 0:
                print "Count " + str (count)

        c.execute ("COMMIT")
        print "Done"
    except Exception as e:
        print "Failed"
        print e
        c.execute ("ROLLBACK")

# this is the main routine, it parses the command line
# parameters and initiates the actions

def process_args (argv):
    # these are the actions to take
    createdb = 0
    commodities = 0
    systems = 0
    stations = 0
    prices = 0

    # parse the arguments here are the options
    try:
        opts, args = getopt.getopt (argv, "hcmstpa", ["createdb", "commodities", "systems", "stations", "prices", "all"])
    except getopt.GetoptError:
        usage ()
    for opt, arg in opts:
        if opt == '-h':
            usage ()
        elif opt in ("-c", "--createdb", "-a", "--all"):
	    # note -c and -a are synonyms
            createdb = 1
            commodities = 1
            systems = 1
            stations = 1
            prices = 1
        elif opt in ("-m", "--commodities"):
            commodities = 1
        elif opt in ("-s", "--systems"):
            systems = 1
        elif opt in ("-t", "--stations"):
            stations = 1
        elif opt in ("-p", "--prices"):
            prices = 1

    # now do the actions
    if createdb:
        do_createdb ()

    if commodities:
        do_commodities ()

    if systems:
        do_systems ()

    if stations:
        do_stations ()

    if prices:
        do_prices ()

    if not createdb and not commodities and not systems and not stations and not prices:
        print 'Nothing to do'
        usage ()

# I keep the schema as the result of a routine
# so it is easy to insert into the db
def getSchema ():
    schema = """CREATE TABLE `stations` (
    `id`    INTEGER NOT NULL,
    `name`    TEXT NOT NULL,
    `system_id`    INTEGER NOT NULL,
    `updated_at`    INTEGER NOT NULL,
    `max_landing_pad_size`    TEXT NOT NULL,
    `distance_to_star`    REAL NOT NULL,
    `is_planetary`    INTEGER NOT NULL,
    PRIMARY KEY(`id`)
);
CREATE INDEX `stations_id` ON `stations` (
    `id`
);
CREATE INDEX `stations_system_id` ON `stations` (
    `system_id`
);
CREATE TABLE `commodities` (
    `id`    INTEGER NOT NULL,
    `name`    TEXT NOT NULL
);
CREATE INDEX `commodities_id` ON `commodities` (
    `id`
);
CREATE INDEX `commodities_name` ON `commodities` (
    `name`
);
CREATE TABLE `prices` (
    `id`    INTEGER NOT NULL,
    `station_id`    INTEGER NOT NULL,
    `commodity_id`    INTEGER NOT NULL,
    `supply`    INTEGER NOT NULL,
    `demand`    INTEGER NOT NULL,
    `buy_price`    INTEGER NOT NULL,
    `sell_price`    INTEGER NOT NULL,
    `collected_at`    INTEGER NOT NULL,
    PRIMARY KEY(`id`)
);
CREATE INDEX `prices_station_id` ON `prices` (
    `station_id`
);
CREATE INDEX `prices_collected_at` ON `prices` (
    `collected_at`
);
CREATE INDEX `prices_commodity_id` ON `prices` (
    `commodity_id`
);
CREATE INDEX `prices_id` ON `prices` (
    `id`,
    `commodity_id`
);
CREATE TABLE IF NOT EXISTS "Systems" (
	`id`	INTEGER NOT NULL,
	`edsm_id`	INTEGER NOT NULL,
	`idx`	INTEGER NOT NULL DEFAULT 0,
	`name`	TEXT NOT NULL,
	`x`	REAL NOT NULL,
	`y`	REAL NOT NULL,
	`z`	REAL NOT NULL,
	`needs_permit`	INTEGER NOT NULL,
	PRIMARY KEY(`id`)
);
CREATE INDEX `systems_name` ON `Systems` (
	`name`
);
CREATE INDEX `systems_edsm_id` ON `Systems` (
	`edsm_id`
);
CREATE INDEX `stations_name` ON `Systems` (
	`name`
);
CREATE INDEX `systems_index_id` ON `Systems` (
	`idx`,
    `id`
);
CREATE INDEX `systems_id` ON `Systems` (
	`id`,
	`idx`
);"""

    return schema

# now call the main routine
process_args(sys.argv[1:])

