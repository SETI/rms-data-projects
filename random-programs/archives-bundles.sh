cd /Volumes/pdsdata-admin/pds4-holdings/bundles

echo ".DS_Store" >X.txt
echo "browse_raw/1*" >>X.txt
echo "data_raw/1*" >>X.txt

echo ".DS_Store" >X1.txt

for DIR in cassini_iss_cruise cassini_iss_saturn cassini_vims_cruise cassini_vims_saturn
do
  mkdir ../archives-bundles/$DIR
  COPYFILE_DISABLE=1 tar cvfz ../archives-bundles/$DIR/$DIR.tar.gz --exclude-from=X.txt $DIR

  for f in $DIR/data_raw/1*
  do
    name=$( basename "$f" )
    echo $DIR/browse_raw/$name
    COPYFILE_DISABLE=1 tar cvfz ../archives-bundles/$DIR/$DIR--browse_raw--$name.tar.gz --exclude-from=X1.txt $DIR/browse_raw/$name $DIR/browse_raw/collection*
    echo $DIR/data_raw/$name
    COPYFILE_DISABLE=1 tar cvfz ../archives-bundles/$DIR/$DIR--data_raw--$name.tar.gz --exclude-from=X1.txt $DIR/data_raw/$name $DIR/browse_raw/collection*
  done
done
