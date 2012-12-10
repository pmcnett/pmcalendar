CREATE TABLE pmcalendar_static (pk CHAR(40) PRIMARY KEY,
                                monthday CHAR(4),
                                diary LONGTEXT);
CREATE INDEX pmcalendar_static_monthday on pmcalendar_static(monthday);

CREATE TABLE pmcalendar_daily (pk CHAR(40) PRIMARY KEY,
                               date DATE,
                               diary LONGTEXT);
CREATE INDEX pmcalendar_daily_date on pmcalendar_daily(date);

