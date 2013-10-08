#!/bin/bash
rm -rf dev.db
for file in `find ./ -name "*.pyc"`
do
        rm -rf $file
done
python manage.py syncdb
python manage.py loaddata fixtures/lpb_project_data.json
python manage.py loaddata fixtures/lpb_resource.json
python manage.py loaddata fixtures/lpb_image_data.json
