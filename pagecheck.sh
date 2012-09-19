#!/bin/bash -x

# monitors a URL for changes, at which point an email is attempted to EMAIL_ADDRESS, then program exits.

URL=$1
EMAIL_ADDRESS=$2

# 

# waits for a url ($1) to 

TMPFILE=/tmp/pagecheck.$$

curl $1 -o $TMPFILE
ORIGINAL_MD5=`md5 $TMPFILE  | awk '{print $NF}'`

sleep 1

curl $1 -o $TMPFILE
NEW_MD5=`md5 $TMPFILE  | awk '{print $NF}'`

while [ $NEW_MD5 = $ORIGINAL_MD5 ]; do
    sleep 60
    curl $1 -o $TMPFILE
    NEW_MD5=`md5 $TMPFILE  | awk '{print $NF}'`
done

echo $1 | mail -s "page $1 is refreshed" $2
