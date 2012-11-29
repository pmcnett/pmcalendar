import datetime
import calendar
import dabo
dabo.ui.loadUI("wx")
from dabo.ui import dPanel, dSizer, dGridSizer, dButton, \
		dEditBox, dTextBox, dControlMixin, callAfterInterval, dKeys
from dabo.lib.dates import goMonth
import biz


class BaseMixin(dControlMixin):
	def initProperties(self):
		self.BorderStyle = None


class EditMixin(BaseMixin):
	def onGotFocus(self, evt):
		# get bizobj on this row
		pass

	def onLostFocus(self, evt):
		# save the changes
		pass


class Day(dButton, BaseMixin):
	def initProperties(self):
		self.Width = 30
		self.Height = 23
		self.Name = "day"
		self.ReadOnly = True
		super(Day, self).initProperties()

	def onKeyDown(self, evt):
		self.Parent.processDayKeyDown(evt)

	def onGotFocus(self, evt):
		print self.Parent.Date


class Static(dTextBox, EditMixin):
	def initProperties(self):
		self.Value = "blah..."
		self.FontItalic = True
		self.Name = "static"
		super(Static, self).initProperties()


class Diary(dEditBox, EditMixin):
	def initProperties(self):
		self.Height = 10
		self.Name = "diary"
		super(Diary, self).initProperties()


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
		if kc not in [dKeys.key_Up, dKeys.key_Down, dKeys.key_Left, dKeys.key_Right]:
			return
		evt.stop()
		if not ctrlDown:
			# move by day, wrapping around in the calendar
			x,y = self.Pos
			if kc == dKeys.key_Up:
				y -= 1
				if y < 0:
					y = 5
			elif kc == dKeys.key_Down:
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


class PnlMonth(dPanel):
	def afterInit(self):
		gs = self.Sizer = dGridSizer(MaxCols=7)
		for y in range(6):
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
		self.Form.Caption = "%s %s" \
				% (current_date.strftime(calendar.month_name.format), self.Year)

	def setDays(self):
		mv = biz.getMonthMatrix(self.Year, self.Month)
		self.date_obj_map = {}
		for y in range(6):
			for x in range(7):
				o = getattr(self, "day_%s_%s" % (x,y))
				o.Date = mv[y][x]
				self.date_obj_map[o.Date] = o

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

		
if __name__ == "__main__":
	app = dabo.dApp(MainFormClass=None)
	app.setup()
	frm = dabo.ui.dForm(None)
	d = PnlMonth(frm)
	frm.Sizer = dSizer("v")
	frm.Sizer.append1x(d)
	frm.show()
	app.start()
