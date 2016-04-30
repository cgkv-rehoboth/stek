#!/bin/bash
echo "---------------------------------"
echo ">> Updating assets"
echo "---------------------------------"
echo

sudo -u rehoboth bash <<EOF
gulp build:prod
. .virtualenv/bin/activate
cd src
./manage.py collectstatic --noinput
EOF

echo "---------------------------------"
echo ">> Done refreshing assets"
echo "---------------------------------"
echo

read -p "Do you want to run migrations?" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
  . .virtualenv/bin/activate
  cd src
  ./manage.py migrate
fi


echo
echo "---------------------------------"
echo ">> Done with migrations"
echo "---------------------------------"
echo

echo ">> We need to restart the uwsgi process"

sudo stop rehoboth
sudo start rehoboth

echo
echo "---------------------------------"
echo ">> Done."
echo "---------------------------------"
