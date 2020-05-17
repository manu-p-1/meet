#!/bin/sh

trap "trap_ctrlc" 2

cancel(){
  read -r -p "Press ENTER to EXIT"
  exit 1
}

trap_ctrlc ()
{
    echo "Ctrl-C caught...performing clean up"
    echo "Killing...$f_pid"
    kill "$f_pid"

    #cleanup the dist folder
    rm -r static/dist/*
    rm -r static/.webassets-cache/*

    if [ ! -z "$(mysql -qfsBe "DROP DATABASE 'mrcdb'; CREATE SCHEMA 'mrcdb'" 2>&1)" ];
    then
      echo "INFO: Success"
    else
      echo "ERROR: mrcdb could not be found on the MySQL instance"
      cancel
    fi

    safe_cancel
}

safe_cancel(){
      # Allow the user to see the message, so sleep for 4 seconds
    echo "Exiting In: "
    for i in 2 1
    do
       echo "$i... "
       sleep 1
    done
    exit 0
}

printf "BASH SCRIPT FOR MRC\n
VERSION 1.0.0\n
AUTHOR: MANU\n
DESCRIPTION: This is a bash script for initiating Flask and MRC. Make sure that you have
MySQL installed locally on your machine. The server.py file requires a username and password.
This script checks if you have them as global environment variables. If not, the script will add
it locally. If your environment variables don't seem to be registering, restart your IDE or terminal."

printf "\n\n"
echo "--------------------------------------------------------------------"
printf "\n\n"

echo "Hello $(whoami)"

if [[ -z "${DB_USER}" ]]; then
  read -r -p "Enter Your MySQL username: "  uname
  export DB_USER=$uname
  echo "exported DB_USER"
fi


if [[ -z "${DB_PASS}" ]]; then
  read -s -r -p "Enter Your MySQL password: "  pwd
  export DB_PASS=$pwd
  echo "exported DB_PASS"
fi

if [ ! -z "`mysql -qfsBe "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='mrcdb'" 2>&1`" ];
then
  mysql -qfsBe "CREATE SCHEMA 'mrcdb'" 2>&1
  echo "INFO: mrcdb registered"
fi

printf "==ALL SQL CHECKS PASSED==\n"

#Using an actual python script in case people have python 2 on their computer too.
version=$(python -c 'import sys; print("".join(map(str, sys.version_info[:3])))')
re='^[0-9]+$'

if [[ -z "$version" || $version =~ re ]];
then
    echo "PYTHON WAS NOT FOUND ON THE SYSTEM."
    cancel
fi

verAsInt=${version//[\.]/}

if ! [[ $verAsInt -ge 370 ]];
then
  echo "PYTHON VERSION IS $version BUT REQUIRES 3.7.5 OR HIGHER"
  cancel
fi

printf "\n==ALL PYTHON CHECKS PASSED==\n\n"

if [[ -z "${DB}" ]]; then
  export DB=mrcdb
  echo "exported DB"
fi

if [[ -z "${DB_HOST}" ]]; then
  export DB_HOST=localhost
  echo "exported DB_HOST"
fi

if [[ -z "${MRC_APP_TOKEN}" ]]; then
  read -r -p "Enter Your Marqeta app token: "  app_token
  export MRC_APP_TOKEN=$app_token
  echo "exported MRC_APP_TOKEN"
fi

if [[ -z "${MRC_ACCESS_TOKEN}" ]]; then
  read -r -p "Enter Your Marqeta access token: "  access_token
  export MRC_ACCESS_TOKEN=$access_token
  echo "exported MRC_ACCESS_TOKEN"
fi

if [[ -z "${MY_ACCESS}" ]]; then
  export MY_ACCESS=abf01008-65c8-4e4b-b950-c30634f37f2f
  echo "exported MY_ACCESS"
fi

if [[ -z "${MY_APP}" ]]; then
  export MY_APP=2ef6b1d8-5a92-4884-9cf6-ae04d02b8fa5
  echo "exported MY_APP"
fi


# DEBUG TRUE - FLASK RESTARTS FOR EVERY CHANGE :)
export FLASK_DEBUG=1
export FLASK_APP=server:create_server

flask run -h 127.0.0.1 &
f_pid=$!

python -mwebbrowser http://127.0.0.1:5000
wait