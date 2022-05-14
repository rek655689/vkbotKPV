from datetime import datetime
import calendar
now = datetime.now()
month = calendar.monthcalendar(now.year, now.month)
sundays = [week[0] for week in month if week[0]>0]
a = sundays[1]
print(a == now.day)