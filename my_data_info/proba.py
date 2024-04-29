from datetime import datetime, timedelta, date



DATE_FORMAT = '%d.%m.%Y'
my_date = '18.09.1985'

birthday = datetime.strptime(my_date, DATE_FORMAT)
print(birthday)
curr_time = datetime.now()
diff_second = (curr_time - birthday).total_seconds()
print(diff_second)
print(datetime.now().year - birthday.year)

print(datetime(5, 1, 1))

# print(datetime(microsecond=100000))