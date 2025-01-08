#!/bin/sh
############################################################################### 

machine=$(hostname -s)

echo 'To: rjw274@psu.edu'		>  MoonsEmail.txt
echo 'From: rjw274@gmail.com'	>> MoonsEmail.txt
echo 'Subject: re: '$3			>> MoonsEmail.txt
echo ''							>> MoonsEmail.txt
echo 'Check '$1' on '$machine', iterations = '$2	>> MoonsEmail.txt

ssh rjw274@nova.astro.psu.edu 'ssmtp -C ~/SSMTP/default.conf racheljworth@gmail.com < ~/Panspermia/newmoons/MoonsEmail.txt'
