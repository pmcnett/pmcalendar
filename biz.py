from dabo.biz import dBizobj

class BizDaily(dBizobj):
	def initProperties(self):
		self.DataSource = "pmcalendar_daily"
		self.DataStructure = (
				# (field_alias, field_type, pk, table_name, field_name, field_scale)
				("date_pk", "D", True, "pmcalendar_daily", "date_pk"),
				("diary", "M", False, "pmcalendar_daily", "diary"),
				)

		self.KeyField = "date_pk"

	def setBaseSQL(self):
		self.addFrom(self.DataSource)
		self.addFieldsFromDataStructure()
		self.addOrderBy("pmcalendar_daily.date_pk")

	def requery_for_dates(self, beg_date, end_date):
		self.setWhereClause("date between ? and ?")
		self.setParams((beg_date, end_date))
		self.requery()

	def requery_for_date(self, date):
		self.requery_for_dates(date, date)



class BizStatic(dBizobj):
	def initProperties(self):
		self.DataSource = "pmcalendar_static"
		self.DataStructure = (
				# (field_alias, field_type, pk, table_name, field_name, field_scale)
				("daymonth", "C", True, "pmcalendar_static", "daymonth"),
				("diary", "M", False, "pmcalendar_static", "diary"),
				)

		self.KeyField = "daymonth"

	def setBaseSQL(self):
		self.addFrom(self.DataSource)
		self.addFieldsFromDataStructure()
		self.addOrderBy("pmcalendar_static.daymonth")

	
