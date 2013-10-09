#!/bin/bash
if [ "$1" = "vt" ]
then
        echo 'reset vt'
        python manage.py reset vt
        python manage.py loaddata fixtures/lpb_image_data.json
elif [ "$1" = "test" ]
then
        echo 'init test data'
        python manage.py loaddata fixtures/lpb_unittest.json
else
        echo 'init db'
        rm -rf dev.db
        for file in `find ./ -name "*.pyc"`
        do
                rm -rf $file
        done
        python manage.py syncdb
        python manage.py loaddata fixtures/lpb_project_data.json
        python manage.py loaddata fixtures/lpb_resource.json
fi
