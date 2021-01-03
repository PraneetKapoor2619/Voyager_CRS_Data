import datetime
def year_fraction(datestr):
    date = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
    start = datetime.date(date.year, 1, 1).toordinal()
    year_length = datetime.date(date.year+1, 1, 1).toordinal() - start
    return date.year + float(date.toordinal() - start) / year_length