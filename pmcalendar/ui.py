import datetime
import calendar
import dabo
dabo.ui.loadUI("wx")
from dabo.ui import dForm, dPanel, dSizer, dGridSizer, dButton, dEditBox, \
                    dTextBox, dControlMixin, callAfterInterval, dKeys, \
                    dLabel, dHyperLink
from dabo.lib.dates import goMonth, goDate
import biz

__all__ = ["FrmCalendar"]


class BaseMixin(dControlMixin):
    """Base behavior for all the relevant controls."""
    def initProperties(self):
        self.BorderStyle = None

    def onGotFocus(self, evt):
        callAfterInterval(10, self.Parent.gotFocus)

    def onLostFocus(self, evt):
        callAfterInterval(10, self.Parent.lostFocus)


class PnlNavigation(dPanel):
    def afterInit(self):
        hs = self.Sizer = dSizer("h")
        but_props = {"FontBold": True, "ShowInBrowser": False,
                     "OnHit": self.onHit_but, "VisitedUnderline": False,
                     "LinkUnderline": False, "VisitedColor": "black",
                     "HoverUnderline": False, "LinkColor": "black"}
        left_but = dHyperLink(self, Name="butLeft", Caption="   <   ", **but_props)
        right_but = dHyperLink(self, Name="butRight", Caption="   >   ", **but_props)
        lbl = dLabel(self, Name="lblMonthYear", FontBold=True)
        hs.appendSpacer(20)
        hs.append(left_but)
        hs.appendSpacer(10)
        hs.append(lbl, alignment="middle")
        hs.appendSpacer(10)
        hs.append(right_but)
        hs.appendSpacer(20)
        
    def setCaption(self, val):
        self.lblMonthYear.Caption = val
        self.layout()
        callAfterInterval(100, self.Parent.Sizer.layout)

    def onHit_but(self, evt):
        pnlLayout = self.Form.pnlLayout
        interval = {"butLeft": -1, "butRight": 1,}[evt.EventObject.Name]
        new_date = goMonth(datetime.date(pnlLayout.Year, pnlLayout.Month, 1),
                           interval)
        pnlLayout.Year = new_date.year
        pnlLayout.Month = new_date.month
        pnlLayout.setFocus()


class DummyTextBox(dTextBox, BaseMixin):
    """Invisible textbox simply to receive and respond to user actions."""
    def initProperties(self):
        ## Dabo doesn't yet offer an interface to set wx.TE_PROCESS_ENTER.
        import wx
        self.Size = (0, 0)
        self._addWindowStyleFlag(wx.TE_PROCESS_ENTER)

    def onKeyDown(self, evt):
        self.Parent.processDayKeyDown(evt)


class EditMixin(BaseMixin):
    """Base behavior for the edit boxes."""
    def initProperties(self):
        super(EditMixin, self).initProperties()
        self.Height = 5
        self.Width = 5
        self.DynamicBackColor = self.getBackColor

    def onLostFocus(self, evt):
        super(EditMixin, self).onLostFocus(evt)
        self.save()

    def save(self):
        """Subclasses must override if they want entered data to be saved."""
        pass

    def getBackColor(self):
        """Color depends on whether this day is in the current month."""
        try:
            return (
                "white" if self.Parent.Date.month == self.Parent.Parent.Month
                else "lightgrey")
        except StandardError:
            return "darkgrey"


class Day(dLabel):
    """The day number in the upper-left of each day panel."""
    def initProperties(self):
        self.Width = 30
        self.Height = 23
        self.Name = "day"
        self.ForeColor = "blue"

    def onMouseLeftClick(self, evt):
        self.Parent.setFocus()

    def onMouseLeftDoubleClick(self, evt):
        self.Parent.diary.setFocus()


class Static(dTextBox, EditMixin):
    """View/edit/save the diary entries that repeat on this day every year."""
    def initProperties(self):
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


class DiaryView(dEditBox, EditMixin):
    """The view of the day's diary (no unneeded scrollbars)."""
    def initProperties(self):
        ## dabo doesn't yet allow overriding the display of scrollbars.
        import wx
        self.Name = "diary"
        self._addWindowStyleFlag(wx.TE_NO_VSCROLL)
        super(DiaryView, self).initProperties()

    def onGotFocus(self, evt):
        """Switch to the edit control (with scrollbars)."""
        edit = self.Parent.diaryedit
        edit.Value = self.Value
        edit.Visible = True
        self.Visible = False
        self.Parent.layout()
        edit.setFocus()

    def onLostFocus(self, evt):
        ## overridden to avoid unneccesary save()
        pass


class DiaryEdit(dEditBox, EditMixin):
    """The editable view of the day's diary (with scrollbars)."""
    def initProperties(self):
        self.Name = "diaryedit"
        self.Visible = False
        super(DiaryEdit, self).initProperties()

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

    def onLostFocus(self, evt):
        super(DiaryEdit, self).onLostFocus(evt)
        view = self.Parent.diary
        view.Value = self.Value
        view.Visible = True
        self.Visible = False
        self.Value = ""
        self.Parent.layout()


class PnlDay(dPanel):
    """Panel of a calendar day, including the day number and edit controls."""
    def initProperties(self):
        self.BorderStyle = "Raised"
        self.DynamicBackColor = self.getBackColor
        self._hadFocus = False

    def afterInit(self):
        self.dummy = DummyTextBox(self)
        vs = self.Sizer = dSizer("v")
        hs = dSizer("h")
        hs.append(Day(self), "expand")
        hs.append1x(Static(self))
        vs.append(hs, "expand")
        vs.append1x(DiaryView(self))
        vs.append1x(DiaryEdit(self))
        parent = self.Parent
        diary = self.diary
        self.key_actions = {
            (dKeys.key_Enter, dKeys.key_Numpad_enter): (diary.setFocus, ()),
            (ord("t"), ord("T")): (parent.setFocusToToday, ()),
            (ord("+"), ord("=")): (self.setFocusToInterval, ("days", 1)),
            (ord("-"),): (self.setFocusToInterval, ("days", -1)),
            (ord("["),): (self.setFocusToInterval, ("months", -1)),
            (ord("]"),): (self.setFocusToInterval, ("months", 1))}

    def gotFocus(self):
        day = self.day
        dummy = self.dummy
        if not self._hadFocus:
            day.FontBold = True
            day.ForeColor = "darkblue"
        self._hadFocus = True
        day.refresh()

    def lostFocus(self):
        if self.Form.ActiveControl not in self.Children:
            self._hadFocus = False
            day = self.day
            day.FontBold = False
            day.ForeColor = "blue"
            self.refresh()

    def setFocus(self):
        self.dummy.setFocus()

    def setFocusToInterval(self, mode, interval):
        """Go forward or backward by months or days."""
        assert mode in ("days", "months")
        func = {"days": goDate, "months": goMonth}[mode]
        date = self.Date
        self.Parent.setFocusToDate(func(date, interval))
    
    def processDayKeyDown(self, evt):
        """User is navigating the calendar; respond appropriately."""
        evtData = evt.EventData
        kc = evtData["keyCode"]
        ctrlDown = evtData["controlDown"]
        layout = self.Form.CalendarLayout
        for keys, func_args in self.key_actions.items():
            if kc in keys:
                func, args = func_args
                func(*args)
                evt.stop()
                return
        if kc not in [dKeys.key_Up, dKeys.key_Down,
                      dKeys.key_Left, dKeys.key_Right]:
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
            new_ctrl.setFocus()
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

    def getBackColor(self):
        try:
            return  ("white" if self.Date.month == self.Parent.Month
                     else "lightgrey")
        except StandardError:
            return "darkgrey"

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
    """Superclass to handle common elements for views (day, month, week)."""
    _week_range = None

    def afterInit(self):
        con = self.Form.Connection
        gs = self.Sizer = dGridSizer(MaxCols=7)
        self.bizStatic = biz.BizStatic(con)
        self.bizDaily = biz.BizDaily(con)
        header = calendar.weekheader(3).split()
        for x in header:
            gs.append(dLabel(self, Caption=x), alignment="center")
        for y in range(self._week_range):
            for x in range(7):
                gs.append(PnlDay(self, Pos=(x,y)), "expand")
                gs.setColExpand(True, x)
            gs.setRowExpand(True, y+1)
        self.setFocusToToday()

    def afterDateChanged(self):
        self.setFormCaption()
        self.setDays()

    def setFormCaption(self):
        current_date = datetime.date(self.Year, self.Month, 1)
        self.Form.setCaption("%s %s" % (
                current_date.strftime(calendar.month_name.format), self.Year))

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
                if bizStatic.locate("%s%s" % (
                        o.Date.month, o.Date.day), "monthday"):
                    o.static.Value = bizStatic.Record.diary
                else:
                    o.static.Value = ""
                if bizDaily.locate(o.Date, "date"):
                    o.diary.Value = bizDaily.Record.diary
                else:
                    o.diary.Value = ""
                self.date_obj_map[o.Date] = o
        self.update()

    def setFocusToToday(self):
        """Requerying the calendar if necessary, place cursor on today."""
        self.setFocusToDate(datetime.date.today())

    def setFocusToDate(self, date):
        """Requerying the calendar if necessary, place cursor on date."""
        try:
            self.date_obj_map[date].setFocus()
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
    """Standard 7x6 month layout."""
    _week_range = 6


class PnlWeek(PnlLayout):
    """7x1 week layout (INCOMPLETE)."""
    _week_range = 1


class FrmCalendar(dForm):
    """The main containing form of the calendar."""
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
        vs = self.Sizer = dSizer("v")
        vs.appendSpacer(5)
        vs.append(PnlNavigation(self, Name="pnlNavigation"), alignment="center")
        vs.appendSpacer(5)
        self.updateLayout()
            
    def updateLayout(self):
        """Draw the calendar on screen depending on self.Layout."""
        pnls = self._instantiatedLayouts
        PnlClass = {"month": PnlMonth, "week": PnlWeek}[self.CalendarLayout]
        vs = self.Sizer
        for pnl in pnls.values():
            pnl.Visible = False
        pnl = self.pnlLayout = pnls.setdefault(PnlClass, PnlClass(self))
        if pnl not in vs.ChildWindows:
            vs.append1x(pnl)
        self.layout()

    def setCaption(self, val):
        appendCaption = self._appendCaption
        if appendCaption:
            appendCaption = "[%s]" % appendCaption
        self.Caption = "%s %s" % (val, appendCaption)
        self.pnlNavigation.setCaption(val)

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
    # If you want Sunday to be the first weekday, you need code like
    # the following commented lines in your application prior to 
    # importing pmcalendar:
    #import calendar
    #calendar.setfirstweekday(6)
    dabo.dApp(MainFormClass=FrmCalendar).start()

