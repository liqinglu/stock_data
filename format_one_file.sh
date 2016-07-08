#!/bin/sh

# delete the last line
lastlinenb=`wc $1 | awk '{print $1}'`
sed -i "${lastlinenb}d" $1

# delete line 1,2
sed -i '1,2d' $1
