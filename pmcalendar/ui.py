__all__ = ["FrmCalendar"]

import datetime
import calendar
import dabo
dabo.ui.loadUI("wx")
from dabo.ui import dForm, dPanel, dSizer, dGridSizer, dButton, \
		dEditBox, dTextBox, dControlMixin, callAfterInterval, dKeys
from dabo.lib.dates import goMonth
import biz


class BaseMixin(dControlMixin):
	def initProperties(self):
		self.BorderStyle = None


class EditMixin(BaseMixin):
	def initProperties(self):
		super(EditMixin, self).initProperties()
		self.Height = 5
		self.Width = 5

	def onLostFocus(self, evt):
		self.save()

	def save(self):
		pass

	def update(self):
		self.BackColor = "white" \
				if self.Parent.Date.month == self.Parent.Parent.Month \
				else "lightgrey"


class Day(dButton, BaseMixin):
	def initProperties(self):
		self.Width = 30
		self.Height = 23
		self.Name = "day"
		self.ReadOnly = True
		super(Day, self).initProperties()

	def onKeyDown(self, evt):
		self.Parent.processDayKeyDown(evt)

	def onHit(self, evt):
		self.Parent.diary.setFocus()


class Static(dTextBox, EditMixin):
	def initProperties(self):
		self.Value = "blah..."
		self.FontItalic = True
		self.Name = "static"
		super(Static, self).initProperties()

	def save(self):
		cal = self.Parent.Parent
		day = self.Parent
		bizStatic = cal.bizStatic
		monthday = "%s%s" % (day.Date.month, day.Date.day)
		if not bizStatic.locate(monthday, "monthday"):
			bizStatic.new()
			bizStatic.Record.monthday = monthday
		bizStatic.Record.diary = self.Value
		bizStatic.save()


class Diary(dEditBox, EditMixin):
	def initProperties(self):
		self.Name = "diary"
		super(Diary, self).initProperties()

	def save(self):
		cal = self.Parent.Parent
		day = self.Parent
		bizDaily = cal.bizDaily
		date = day.Date
		if not bizDaily.locate(date, "date"):
			bizDaily.new()
			bizDaily.Record.date = date
		bizDaily.Record.diary = self.Value
		bizDaily.save()


class PnlDay(dPanel):
	def initProperties(self):
		self.BorderStyle = "Raised"

	def afterInit(self):
		vs = self.Sizer = dSizer("v")
		hs = dSizer("h")
		hs.append(Day(self), "expand")
		hs.append1x(Static(self))
		vs.append(hs, "expand")
		vs.append1x(Diary(self))

	def processDayKeyDown(self, evt):
		evtData = evt.EventData
		kc = evtData["keyCode"]
		ctrlDown = evtData["controlDown"]
		layout = self.Form.CalendarLayout
		if kc not in [dKeys.key_Up, dKeys.key_Down, dKeys.key_Left, dKeys.key_Right]:
			return
		evt.stop()
		if not ctrlDown:
			# move by day, wrapping around in the calendar
			x,y = self.Pos
			if kc == dKeys.key_Up and layout in ("month",):
				y -= 1
				if y < 0:
					y = 5
			elif kc == dKeys.key_Down and layout in ("month",):
				y += 1
				if y > 5:
					y = 0
			elif kc == dKeys.key_Left:
				x -= 1
				if x < 0:
					x = 6
			elif kc == dKeys.key_Right:
				x += 1
				if x > 6:
					x = 0
			new_ctrl = getattr(self.Parent, "day_%s_%s" % (x,y))
			new_ctrl.day.setFocus()
		else:
			year, month = self.Parent.Year, self.Parent.Month
			current_date = datetime.date(year, month, 1)
			if kc == dKeys.key_Left:
				new_date = goMonth(current_date, -1)
			elif kc == dKeys.key_Right:
				new_date = goMonth(current_date, 1)
			elif kc == dKeys.key_Up:
				new_date = goMonth(current_date, -12)
			elif kc == dKeys.key_Down:
				new_date = goMonth(current_date, 12)
			self.Parent.Year = new_date.year
			self.Parent.Month = new_date.month

	def _getPos(self):
		return self._pos

	def _setPos(self, val):
		self._pos = val
		self.Name = "day_%s_%s" % val

	def _getDate(self):
		return self._date

	def _setDate(self, val):
		self._date = val
		self.day.Caption = str(val.day)

	Pos = property(_getPos, _setPos)
	Date = property(_getDate, _setDate)


class PnlLayout(dPanel):
	_week_range = None

	def afterInit(self):
		con = self.Form.Connection
		gs = self.Sizer = dGridSizer(MaxCols=7)
		self.bizStatic = biz.BizStatic(con)
		self.bizDaily = biz.BizDaily(con)
		for y in range(self._week_range):
			for x in range(7):
				gs.append(PnlDay(self, Pos=(x,y)), "expand")
		gs.setFullExpand()
		today = datetime.date.today()
		self.setFocusToDate(today)

	def afterDateChanged(self):
		self.setFormCaption()
		self.setDays()

	def setFormCaption(self):
		current_date = datetime.date(self.Year, self.Month, 1)
		self.Form.setCaption("%s %s" \
				% (current_date.strftime(calendar.month_name.format), self.Year))

	def setDays(self):
		mv = biz.getMonthMatrix(self.Year, self.Month)
		bizStatic = self.bizStatic
		bizStatic.requery()
		bizDaily = self.bizDaily
		bizDaily.requery_for_dates(mv[0][0], mv[-1][-1])
		self.date_obj_map = {}
		for y in range(self._week_range):
			for x in range(7):
				o = getattr(self, "day_%s_%s" % (x,y))
				o.Date = mv[y][x]
				if bizStatic.locate("%s%s" % (o.Date.month, o.Date.day), "monthday"):
					o.static.Value = bizStatic.Record.diary
				else:
					o.static.Value = ""
				if bizDaily.locate(o.Date, "date"):
					o.diary.Value = bizDaily.Record.diary
				else:
					o.diary.Value = ""
				self.date_obj_map[o.Date] = o
		self.update()

	def setFocusToDate(self, date):
		try:
			self.date_obj_map[date].day.setFocus()
		except (KeyError, AttributeError):
			self.Year = date.year
			self.Month = date.month
			callAfterInterval(75, self.setFocusToDate, date)

	def _getMonth(self):
		return self._month

	def _setMonth(self, val):
		self._month = val
		callAfterInterval(50, self.afterDateChanged)

	def _getYear(self):
		return self._year

	def _setYear(self, val):
		self._year = val
		callAfterInterval(50, self.afterDateChanged)

	Month = property(_getMonth, _setMonth)
	Year = property(_getYear, _setYear)


class PnlMonth(PnlLayout):
	_week_range = 6


class PnlWeek(PnlLayout):
	_week_range = 1


class FrmCalendar(dForm):
	def afterInit(self):
		self._appendCaption = ""
		dcon = self.Connection
		if dcon is None:
			# use in-memory test sqlite database
			dcon = self.Connection = dabo.db.connect(":memory:")
			con = dcon._connection
			con.executescript(open("./create_tables.sql").read())
			self._appendCaption = "Temporary Database"
		self._instantiatedLayouts = {}
		self.Sizer = dSizer("v")
		self.updateLayout()
			
	def updateLayout(self):
		"""Draw the calendar on screen depending on self.Layout."""
		pnls = self._instantiatedLayouts
		PnlClass = {"month": PnlMonth, "week": PnlWeek}[self.CalendarLayout]
		vs = self.Sizer
		for pnl in pnls.values():
			pnl.Visible = False
		pnl = pnls.setdefault(PnlClass, PnlClass(self))
		if pnl not in vs.ChildWindows:
			vs.append1x(pnl)
		self.layout()

	def setCaption(self, val):
		appendCaption = self._appendCaption
		if appendCaption:
			appendCaption = "[%s]" % appendCaption
		self.Caption = "%s %s" % (val, appendCaption)

	def _getConnection(self):
		return getattr(self, "_connection", None)

	def _setConnection(self, val):
		self._connection = val

	def _getCalendarLayout(self):
		return getattr(self, "_calendar_layout", "month")

	def _setCalendarLayout(self, val):
		self._calendar_layout = val
		assert val in ("month", "week")
		dabo.ui.callAfterInterval(10, self.updateLayout())

	
	CalendarLayout = property(_getCalendarLayout, _setCalendarLayout, None,
			"""Either "month" or "week".""")

	Connection = property(_getConnection, _setConnection, None,
			"Dabo dConnection instance.")


if __name__ == "__main__":
	dabo.dApp(MainFormClass=FrmCalendar).start()
