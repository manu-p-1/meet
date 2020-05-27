#!/bin/sh

trap "trap_ctrlc" 2
trap "trap_ctrlslash" 3

cancel(){
  read -r -p "Press ENTER to EXIT"
  exit 1
}

trap_ctrlslash(){
    printf "===Ctrl-C caught....Restarting start.sh===\n\n"
    kill "$f_pid"
    exec "./start.sh" command
}

trap_ctrlc ()
{
    echo "===Ctrl-C caught....performing clean up==="
    kill_flask

    #cleanup the dist folder
    rm -r static/dist/*
    rm -r static/.webassets-cache/*

    drop_schema

    printf "===DROPPED meetdb===\n\n"
    safe_cancel
}

kill_flask(){
  printf "===Killing PID $f_pid....===\n\n"
  kill "$f_pid"
}

drop_schema(){
   if [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]
    then
      echo "Running DB DROP script...."
      /c/Program\ Files/MySql/MySQL\ Server\ 8.0/bin/mysql -u "${DB_USER}" -p"${DB_PASS}" < db/MEET_DROP.sql
    else
      echo "Running DB DROP script...."
      mysql -u "$DB_USER" -p"${DB_PASS}" < ./db/MEET_DROP.sql
    fi
}

safe_cancel(){
      # Allow the user to see the message, so sleep for 4 seconds
    echo "Exiting In: "
    for i in 3 2 1
    do
       echo "$i... "
       sleep 1
    done
    exit 0
}

printf "BASH SCRIPT FOR MEET\n
VERSION 1.0.0\n
AUTHOR: MANU\n
DESCRIPTION: This is a bash script for initiating Flask and MEET. Make sure that you have
MySQL installed locally on your machine. The server.py file requires a username and password.
This script checks if you have them as global environment variables. If not, the script will add
it locally. If your environment variables don't seem to be registering, restart your IDE or terminal."

printf "\n\n"
echo "--------------------------------------------------------------------"
printf "\n\n"

printf "Hello $(whoami)\n\n"

if [[ -z "${DB_USER}" ]]; then
  read -r -p "Enter Your MySQL username: "  uname
  export DB_USER=$uname
  echo "===exported DB_USER==="
fi


if [[ -z "${DB_PASS}" ]]; then
  read -s -r -p "Enter Your MySQL password: "  pwd
  export DB_PASS=$pwd
  printf "===exported DB_PASS===\n\n"
fi

printf "===CREATED: meetdb===\n\n"

if [[ -z "${DB}" ]]; then
  export DB=meetdb
  echo "===exported DB==="
fi

if [[ -z "${DB_HOST}" ]]; then
  export DB_HOST=localhost
  echo "===exported DB_HOST==="
fi

if [[ -z "${MY_ACCESS}" ]]; then
  export MY_ACCESS=abf01008-65c8-4e4b-b950-c30634f37f2f
  echo "===exported MY_ACCESS==="
fi

if [[ -z "${MY_APP}" ]]; then
  export MY_APP=2ef6b1d8-5a92-4884-9cf6-ae04d02b8fa5
  printf "===exported MY_APP==="
fi

if [[ -z "${SAM_CARD_PRODUCT_TOKEN}" ]]; then
  export SAM_CARD_PRODUCT_TOKEN=f39eb05d-76c0-48dd-ac50-d1e4d20b7eab
  printf "===exported SAM_CARD_PRODUCT_TOKEN===\n"
fi

# DEBUG TRUE - FLASK RESTARTS FOR EVERY CHANGE :)
export FLASK_DEBUG=0
export FLASK_APP=server:create_server

printf "===exported FLASK_DEBUG and FLASK_APP===\n\n"

flask run --host=localhost --port=12000 &
f_pid=$!

printf "===Running Flask===\n\n"
echo "Starting Browser...."

python -mwebbrowser http://localhost:12000/
wait