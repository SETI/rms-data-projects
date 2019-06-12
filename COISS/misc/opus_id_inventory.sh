for FILE in "$@";
do
    sed -e "s|./IMG/CO/ISS/\(..........\)/N|co-iss-n\1|" \
        -e "s|./IMG/CO/ISS/\(..........\)/W|co-iss-w\1|" \
        -ixx $FILE
done
