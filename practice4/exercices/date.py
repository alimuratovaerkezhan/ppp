#1
from datetime import datetime, timedelta
current_date = datetime.now()
result_date = current_date - timedelta(days=5)
print("Current Date:", current_date.strftime("%Y-%m-%d"))
print("5 Days Ago:  ", result_date.strftime("%Y-%m-%d"))

#2
from datetime import datetime, timedelta
today = datetime.now().date()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
print(f"Yesterday: {yesterday}")
print(f"Today:     {today}")
print(f"Tomorrow:  {tomorrow}")


#3
from datetime import datetime
dt = datetime.now()
dt_clean = dt.replace(microsecond=0)
print("With Microseconds:   ", dt)
print("Without Microseconds:", dt_clean)


#4
from datetime import datetime
date1 = datetime(2026, 2, 28, 12, 0, 0) # Feb 28, 2026 at Noon
date2 = datetime(2026, 2, 25, 10, 30, 0) # Feb 25, 2026 at 10:30 AM
difference = date1 - date2
seconds_diff = difference.total_seconds()
print(f"Difference: {seconds_diff} seconds")