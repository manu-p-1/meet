drop_schema(){
   if [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]
    then
      echo "Running DB DROP script...."
      /c/Program\ Files/MySql/MySQL\ Server\ 8.0/bin/mysql -u "${DB_USER}" -p"${DB_PASS}" < db/MRC_DROP.sql
    else
      echo "Running DB DROP script...."
      mysql -u "$DB_USER" -p"${DB_PASS}" < ./db/MRC_DROP.sql
    fi
}

create_schema(){
  if [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]
  then
    printf "Running DB creation script...."
    /c/Program\ Files/MySql/MySQL\ Server\ 8.0/bin/mysql -u "${DB_USER}" -p"${DB_PASS}" < db/MRC1.1.sql
  else
    printf "Running DB creation script...."
    mysql -u "${DB_USER}" -p"${DB_PASS}" < ./db/MRC1.1.sql
  fi
}

printf "===Running startdb.sh===\n\n"

drop_schema
create_schema