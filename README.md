Python script(s) to maintain and work with a SQLite DB of Elite Dangerous information

 EliteTradeSearchPySqlite

 This is a set of scripts that contain information that helps playing the
 game Elite Dangerous.

 EliteTradeSearchPySqlite/updatedb.py

 This is one script of hopefully many that allow you to download the latest
 information from the Eddb.io site about the commodities, star systems, space
 stations, and commodity prices at those stations.   This script will
 download those files and insert them into a SQLite database for easy
 perusal.  The data gets old quickly, use this script to keep the database
 relevant for searching.

 Note: this should always be run in the EliteTradeSearchPySqlite directory as
 all of its's sister scripts and files will be located here.  This file may
 contain upwards of 20 gigs during operations.

 The files and format that this script downloads and inserts into the
 SQLiteDB.

 https://eddb.io/archive/v5/commodities.json

 This file is in JSON format and here are just a few lines from a typical
 download.

 ```[
   {
      "ed_id" : 128672162,
      "is_rare" : 0,
      "min_sell_price" : 1298,
      "sell_price_upper_average" : 13368,
      "is_non_marketable" : 0,
      "max_sell_price" : 15769,
      "max_buy_price" : null,
      "min_buy_price" : null,
      "average_price" : 11912,
      "id" : 334,
      "category_id" : 16,
      "buy_price_lower_average" : 0,
      "category" : {
         "name" : "Salvage",
         "id" : 16
      },
      "name" : "Gene Bank"
   },
```

   From the commodities file we are mostly interested in just the name and
   id, the id is used as a foreign key in the db.

 https://eddb.io/archive/v5/systems_populated.jsonl

    This is a jsonl file, where each line is a complete json object, read
    each line in one at a time, parse and insert.

```
{"id":1,"edsm_id":12695,"name":"1 G. Caeli","x":80.90625,"y":-83.53125,"z":-30.8125,"population":6544826,"is_populated":true,"government_id":144,"government":"Patronage","allegiance_id":2,"allegiance":"Empire","state_id":16,"state":"Boom","security_id":32,"security":"Medium","primary_economy_id":4,"primary_economy":"Industrial","power":"Arissa Lavigny-Duval","power_state":"Exploited","power_state_id":32,"needs_permit":false,"updated_at":1536002636,"simbad_ref":"","controlling_minor_faction_id":31816,"controlling_minor_faction":"1 G. Caeli Empire League","reserve_type_id":3,"reserve_type":"Common","minor_faction_presences":[{"minor_faction_id":31816,"state_id":16,"influence":69.1692,"state":"Boom"},{"minor_faction_id":54517,"state_id":80,"influence":3.5035,"state":"None"},{"minor_faction_id":54518,"state_id":80,"influence":1.1011,"state":"None"},{"minor_faction_id":54519,"state_id":80,"influence":6.4064,"state":"None"},{"minor_faction_id":74917,"state_id":80,"influence":5.1051,"state":"None"},{"minor_faction_id":40897,"state_id":80,"influence":11.1111,"state":"None"},{"minor_faction_id":4017,"state_id":80,"influence":3.6036,"state":"None"}]}
```

 https://eddb.io/archive/v5/stations.jsonl
    This is a jsonl file, where each line is a complete json object, read
    each line in one at a time, parse and insert.

```
{"id":5,"name":"Reilly Hub","system_id":396,"updated_at":1535563693,"max_landing_pad_size":"L","distance_to_star":171,"government_id":64,"government":"Corporate","allegiance_id":3,"allegiance":"Federation","state_id":80,"state":"None","type_id":8,"type":"Orbis Starport","has_blackmarket":false,"has_market":true,"has_refuel":true,"has_repair":true,"has_rearm":true,"has_outfitting":true,"has_shipyard":true,"has_docking":true,"has_commodities":true,"import_commodities":["Pesticides","Aquaponic Systems","Biowaste"],"export_commodities":["Mineral Oil","Fruit and Vegetables","Grain"],"prohibited_commodities":["Narcotics","Tobacco","Combat Stabilisers","Imperial Slaves","Slaves","Personal Weapons","Battle Weapons","Bootleg Liquor","Landmines"],"economies":["Agriculture"],"shipyard_updated_at":1535909043,"outfitting_updated_at":1535909043,"market_updated_at":1535909042,"is_planetary":false,"selling_ships":["Adder","Eagle Mk. II","Federal Dropship","Hauler","Sidewinder Mk. I","Viper Mk III","Cobra MK IV"],"selling_modules":[738,739,740,743,744,745,748,749,750,753,754,755,758,759,760,793,794,795,796,797,824,826,828,837,838,840,843,851,876,877,878,879,880,882,883,884,886,888,891,892,893,896,897,898,927,928,929,932,933,936,937,938,941,942,946,948,961,962,963,964,966,967,968,998,999,1003,1004,1007,1008,1012,1013,1016,1017,1018,1021,1022,1023,1027,1032,1036,1037,1038,1039,1041,1042,1043,1046,1047,1048,1066,1071,1072,1116,1117,1118,1119,1121,1122,1123,1132,1136,1137,1138,1181,1182,1186,1191,1192,1193,1194,1195,1196,1197,1200,1201,1202,1203,1204,1205,1207,1208,1209,1213,1214,1242,1243,1244,1245,1246,1286,1306,1307,1310,1311,1317,1320,1324,1325,1326,1327,1373,1375,1377,1379,1381,1417,1518,1519,1520,1523,1524,1525,1526,1527,1528,1529,1530,1531,1532,1533,1534,1535,1544,1545,1577,1579,1581,1583,1585,1587,1597,1609,1657],"settlement_size_id":null,"settlement_size":null,"settlement_security_id":null,"settlement_security":null,"body_id":7086578,"controlling_minor_faction_id":13925}
```

 https://eddb.io/archive/v5/listings.csv

 This is a CSV file of the price of commodities at all the stations.

```
id,station_id,commodity_id,supply,supply_bracket,buy_price,sell_price,demand,demand_bracket,collected_at
1,1,5,0,0,0,744,1185,3,1535999254
```
