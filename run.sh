#!/bin/bash
for file in `find ./ -name "*.pyc"`
do
        rm -rf $file
done
python manage.py runserver 0.0.0.0:8000
