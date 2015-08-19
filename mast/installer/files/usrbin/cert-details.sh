#!/usr/bin/bash
echo appliance,domain,object,filename,common_name,not_before,not_after,issuer

cd $1
for x in $(find $2 -type f)
do
  # output the appliance and domain seperated by commas
  echo -n $x | cut -d \/ -f 2-3 --output-delimiter="," | xargs echo -n ; echo -n ,

  # output object name and filename
  echo -n $x | cut -d \/ -f 4 | awk -F "_-_" '{ print $1 "," $2 }' | xargs echo -n; echo -n ,

  # output the common name
  openssl x509 -noout -subject -in $x | awk -F "CN=" '{ print $2 "," }' | xargs echo -n 

  # output the not_before date
  openssl x509 -startdate -noout -in $x | cut -d \= -f 2 | xargs echo -n; echo -n ,

  # output the expiration date of the certificate
  openssl x509 -enddate -noout -in $x | cut -d \= -f 2 | xargs echo -n; echo -n ,

  # output the issuer
  echo -n \"; openssl x509 -noout -issuer -in $x | awk -F "issuer=" '{ print $2  }' | xargs echo -n; echo \"
done


