#!/bin/sh

sql="property.sql"
db="property.db"

cp $db backup.db
rm -f $db
sqlite3 -init $sql $db
chmod 666 $db

echo 'Done.'