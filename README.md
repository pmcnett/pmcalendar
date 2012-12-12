pmcalendar
==========

Cross-platform desktop calendar applet that supports multiple database backends.


Features
--------

* Runs on Linux, Mac, and Windows
* Desktop GUI calendar with month, week, and day views (week and day: TODO).
* Corresponding PDF reports with month, week, and day views (TODO).
* Very simple to use.
* User can enter static and diary entries for each day.
* Multiple database backends supported (MySQL, SQLite, PostgreSQL) (Not tested on PostgreSQL yet; other backends should work, too)
* Can be used as a stand-alone application, or as a library to be imported and used in your larger application.


Requirements
------------

* Python 2.6.5 or higher
* wxPython 2.8.12.1 or higher
* Dabo 0.9.4 or higher
* Reportlab 2.1 or higher (if running PDF reports)
* PIL (if running PDF reports)


Screenshots
-----------
* <a href="https://raw.github.com/pmcnett/pmcalendar/master/screenshots/screenshot_mac.png">Mac</a>
* <a href="https://raw.github.com/pmcnett/pmcalendar/master/screenshots/screenshot_windows.png">Windows</a>
* <a href="https://raw.github.com/pmcnett/pmcalendar/master/screenshots/screenshot_linux.png">Linux</a>


Run the demo
------------

After installing and confirming the above prerequisites were installed:

    cd pmcalendar
    python ui.py

This will run it with an in-memory database automatically created for you.


Keyboard Navigation
-------------------

When a day number has the focus, type:

* t: go to today
* -: go to yesterday
* +: go to tomorrow
* [: go to this day last month
* ]: go to this day next month

The arrow keys move you around in the currently displayed calendar, wrapping around the edges. Holding &lt;ctrl&gt; down while navigating with the arrow keys will do the following:

* &lt;ctrl&gt;&lt;up-or-down&gt;: go to prior or next year, leaving cursor on the same calendar position.
* &lt;ctrl&gt;&lt;left-or-right&gt;: go to prior or next month, leaving cursor on the same calendar position.


Use it in your application
--------------------------

Put it in your PYTHONPATH. I have the pmcalendar package under /home/pmcnett/pmcalendar and so I add a .pth file to my `/usr/local/lib/python2.6/dist-packages` directory that says `/home/pmcnett/pmcalendar`.

Then use the create_tables.sql to add the required tables to your database, and add code to your application like:

```python
from pmcalendar.ui import FrmCalendar
app = self.Application  ## (in a Dabo app where self is any dObject)
con = app.dbConnection  ## (whatever dConnection your app uses)
frmCalendar = FrmCalendar(self, Connection=con)
frmCalendar.show()
```
