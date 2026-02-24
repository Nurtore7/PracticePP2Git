from datetime import datetime, timedelta

today = datetime.now()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)

print("Yesterday:", yesterday.strftime("%Y-%m-%d %H:%M:%S"))
print("Today:", today.strftime("%Y-%m-%d %H:%M:%S"))
print("Tomorrow:", tomorrow.strftime("%Y-%m-%d %H:%M:%S"))