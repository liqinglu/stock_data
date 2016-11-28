#!/bin/sh

ls data/*.txt |awk -F"[#.]" '{print $2}' > .inidata
cat > stockpool.ini < .inidata
