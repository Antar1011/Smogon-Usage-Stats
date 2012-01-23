#!/bin/bash

sqlite3 $1 <<!
.headers on
.mode csv
.output $3
select * from $2;
!
