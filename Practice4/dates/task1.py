from datetime import datetime, timedelta

today = datetime.now().replace(microsecond=0)
five_days_ago = (today - timedelta(days=5)).replace(microsecond=0)

print("Today:", today)
print("Five days ago:", five_days_ago)