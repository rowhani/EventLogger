# EventLogger

EventLogger is an application that allows you to log different events during your life. It is targeted for Iranian users.

## Installation

### 1. virtualenv / virtualenvwrapper
You should already know what is [virtualenv](http://www.virtualenv.org/), preferably [virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/) at this stage:

`$ mkvirtualenv --clear eventlogger`

### 2. Download
Now, you need the *EventLogger* project files in your workspace:

    $ cd /path/to/your/workspace
    $ git clone git@github.com:artmansoft/EventLogger.git eventlogger && cd eventlogger

### 3. Requirements
Right there, you will find the *requirements.txt* file that has all the great debugging tools, django helpers and some other cool stuff. To install them, simply type:

`$ pip install -r requirements.txt`

### 4. Tweaks

#### wsgihandler.py
`wsgihandler.py` file is necessary for WSGI gateways (such as uWSGI) to run your Django application and also required from Django itself.

#### Initialize the database
Run the following to install the database

`./manage.py syncdb` and `./manage.py migrate`

### Ready? Go!

`./manage.py runserver`

or

`./manage.py runserver_plus`
