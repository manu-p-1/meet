from datetime import datetime
from typing import Union


class MRCDateRangeParser(object):
    AM = "AM"
    PM = "PM"

    """
    MRC Date Range Parser init
    
    :param mrc_daterange - The date range as a string
    """

    def __init__(self, mrc_daterange: str):
        self._raw_range = mrc_daterange
        self._start_date = None
        self._start_hour = None
        self._start_tod = None
        self._end_date = None
        self._end_hour = None
        self._end_tod = None

    """
    Parses the date and sets properties to retrieve from
    """

    def parse(self):
        splitted_date = self._raw_range.split("-")
        if len(splitted_date) != 2:
            raise MRCDateRangeException("Range must have start and end date", self._raw_range)

        start_range = splitted_date[0].strip()
        end_range = splitted_date[1].strip()

        r = self._parse_range(start_range)
        self._start_date = r[0]
        self._start_hour = r[1]
        self._start_tod = r[2]

        e = self._parse_range(end_range)
        self._end_date = e[0]
        self._end_hour = e[1]
        self._end_tod = e[2]

    def _parse_range(self, daterange: str) -> []:
        range_splitted = daterange.split(" ")

        if len(range_splitted) < 2:
            raise MRCDateRangeException("Malformed Date Range", daterange)

        _datetime = range_splitted[0] + " " + range_splitted[1]

        if len(range_splitted) != 3:
            raise MRCDateRangeException("Malformed Date Range", daterange)

        try:
            datetime.strptime(_datetime, "%m/%d/%Y %H:%M")
        except ValueError:
            raise MRCDateRangeException("Malformed Date Rangedd", _datetime)

        if range_splitted[2].strip() != self.AM and range_splitted[2].strip() != self.PM:
            raise MRCDateRangeException("Time of day not supported", range_splitted[2])

        return range_splitted

    @property
    def start_date(self) -> Union[str, None]:
        if self._start_date is None:
            print("Try running parse() first")
        return self._start_date

    @property
    def start_hour(self) -> Union[str, None]:
        if self._start_hour is None:
            print("Try running parse() first")
        return self._start_hour

    @property
    def start_time_of_day(self) -> Union[str, None]:
        if self._start_tod is None:
            print("Try running parse() first")
        return self._start_tod

    @property
    def end_date(self) -> Union[str, None]:
        if self._end_date is None:
            print("Try running parse() first")
        return self._end_date

    @property
    def end_hour(self) -> Union[str, None]:
        if self._end_hour is None:
            print("Try running parse() first")
        return self._end_hour

    @property
    def end_time_of_day(self) -> Union[str, None]:
        if self._end_tod is None:
            print("Try running parse() first")
        return self._end_tod

    def __repr__(self):
        return f"<{self.__class__.__name__} object({self._raw_range})>"

    def __str__(self):
        return f"""
        start date: {self._start_date}
        start time: {self._start_hour}
        start time of day: {self._start_tod}
        end date: {self._end_date}
        end time: {self._end_hour}
        end time of day: {self._end_tod}
        """


class MRCDateRangeException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
