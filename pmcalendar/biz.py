__all__ = ["BizStatic", "BizDaily"]

import datetime
import calendar
from dabo.biz import dBizobj
from dabo.lib.dates import goMonth
from dabo.lib import getRandomUUID


class BizBase(dBizobj):
	"""Superclass with common behaviors and properties."""
	def initProperties(self):
		self.AutoPopulatePK = False
		self.AutoQuoteNames = False
		self.DefaultValues["pk"] = getRandomUUID
		self.KeyField = "pk"

	def save(self):
		if not self.Record.diary:
			self.delete()
		else:
			super(BizBase, self).save()


class BizDaily(BizBase):
	"""The diary entries for each day."""
	def initProperties(self):
		super(BizDaily, self).initProperties()
		self.DataSource = "pmcalendar_daily"
		self.DataStructure = (
				# (field_alias, field_type, pk, table_name, field_name, field_scale)
				("pk", "C", True, "pmcalendar_daily", "pk"),
				("date", "D", False, "pmcalendar_daily", "date"),
				("diary", "M", False, "pmcalendar_daily", "diary"),
				)

	def setBaseSQL(self):
		self.addFrom(self.DataSource)
		self.addFieldsFromDataStructure()
		self.addOrderBy("pmcalendar_daily.date")

	def requery_for_dates(self, beg_date, end_date):
		self.setWhereClause("date between ? and ?")
		self.setParams((beg_date, end_date))
		self.requery(convertQMarks=True)

	def requery_for_date(self, date):
		self.requery_for_dates(date, date)


class BizStatic(BizBase):
	"""The diary entries that repeat for this day every year."""
	def initProperties(self):
		super(BizStatic, self).initProperties()
		self.DataSource = "pmcalendar_static"
		self.DataStructure = (
				# (field_alias, field_type, pk, table_name, field_name, field_scale)
				("pk", "C", True, "pmcalendar_static", "pk"),
				("monthday", "C", True, "pmcalendar_static", "monthday"),
				("diary", "M", False, "pmcalendar_static", "diary"),
				)


	def setBaseSQL(self):
		self.addFrom(self.DataSource)
		self.addFieldsFromDataStructure()
		self.addOrderBy("pmcalendar_static.monthday")


def getMonthMatrix(year, month):
	"""Return matrix of dates in the month in the 7x6 format."""
	matrix = calendar.monthcalendar(year, month)
	blank_week = [0,0,0,0,0,0,0]
	last_month = goMonth(datetime.date(year, month, 1), -1)
	next_month = goMonth(datetime.date(year, month, 1), 1)
	last_month_day = calendar.monthrange(last_month.year, last_month.month)[1]
	next_month_day = 1
	first_week = matrix[0]
	for idx in range(6, -1, -1):
		if first_week[idx] == 0:
			first_week[idx] = datetime.date(last_month.year, last_month.month, last_month_day)
			last_month_day -= 1
	for week_idx in range(0, 6):
		try:
			week = matrix[week_idx]
		except IndexError:
			week = list(blank_week)
			matrix.append(week)
		for day_idx, day in enumerate(week):
			if isinstance(day, datetime.date):
				continue
			if day == 0:
				week[day_idx] = datetime.date(next_month.year, next_month.month, next_month_day)
				next_month_day += 1
				continue
			# current month and year
			week[day_idx] = datetime.date(year, month, day)
	return matrix

