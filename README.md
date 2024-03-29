# Planetarium Service API

Django project for create API app for Planetarium

## Installation

Python3 and Django must be already installed


```shell
git clone https://github.com/Dobryk12/py-planetarium-service.git
python3 -m venv venv
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Features 

* You can create superuser by your own, or use which is already exist:

* Also you can download data from print_phrase_db_data.json, by using command:
```python manage.py loaddata data_for_load.json```

- After loading data from fixture you can use following superuser:
  - Login: `stan@mate.com`
  - Password: `stan123`
