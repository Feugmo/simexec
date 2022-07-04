#!/bin/bash

## credentials to connect to the pg server (pghost and pgport only required to connect to a remote server)
pguser="postgres"   	# default pg username
pgdb="postgres"	    	# default pg database name
pghost="localhost" 	# local server: localhost; ip address or host name for the remote server
pgport="5432"       	# default port: 5432
pgpass="abc"      	# put your postgres password here
runserver="local"       # connectiion flag: "local": connect to a local pgserver, "remote": connect to a local server


## required to create a role and database for map_simulation_manager
dbuser="map_sim"        # DO NOT change this value
dbname="map_remote_simulation" # DO NOT change this value
dbpass="password"       # set your desired password


scriptdir=`pwd`/src
bash "$scriptdir/make_db.sh" $pguser $pgdb $pghost $pgport $pgpass $dbuser $dbname $dbpass $runserver
