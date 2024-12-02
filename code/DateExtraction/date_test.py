import unittest
import dateExtraction as de
from datetime import date, datetime

class TestDateExtraction(unittest.TestCase):

    PARSER_TEST_CASES = [
    ("Thu Sep 25 10:36:28 2003", datetime(2003, 9, 25, 10, 36, 28), "date command format strip"),   #25/09/2010
    ("Thu Sep 25 2003", datetime(2003, 9, 25), "date command format strip"),        
    ("2003-09-25T10:49:41", datetime(2003, 9, 25, 10, 49, 41), "iso format strip"),
    ("2003-09-25T10:49", datetime(2003, 9, 25, 10, 49), "iso format strip"),
    ("2003-09-25T10", datetime(2003, 9, 25, 10), "iso format strip"),
    ("2003-09-25", datetime(2003, 9, 25), "iso format strip"),
    ("20030925T104941", datetime(2003, 9, 25, 10, 49, 41), "iso stripped format strip"),    #[]
    ("20030925T1049", datetime(2003, 9, 25, 10, 49, 0), "iso stripped format strip"),           #[]
    ("20030925T10", datetime(2003, 9, 25, 10), "iso stripped format strip"),            #[]
    ("20030925", datetime(2003, 9, 25), "iso stripped format strip"),                   #[]
    ("2003-09-25 10:49:41,502", datetime(2003, 9, 25, 10, 49, 41, 502000), "python logger format"),
    ("199709020908", datetime(1997, 9, 2, 9, 8), "no separator"),               #[]
    ("19970902090807", datetime(1997, 9, 2, 9, 8, 7), "no separator"),          #[]
    ("09-25-2003", datetime(2003, 9, 25), "date with dash"),
    ("25-09-2003", datetime(2003, 9, 25), "date with dash"),
    ("10-09-2003", datetime(2003, 10, 9), "date with dash"),
    ("10-09-03", datetime(2003, 10, 9), "date with dash"),
    ("2003.09.25", datetime(2003, 9, 25), "date with dot"),
    ("09.25.2003", datetime(2003, 9, 25), "date with dot"),
    ("25.09.2003", datetime(2003, 9, 25), "date with dot"),
    ("10.09.2003", datetime(2003, 10, 9), "date with dot"),
    ("10.09.03", datetime(2003, 10, 9), "date with dot"),
    ("2003/09/25", datetime(2003, 9, 25), "date with slash"),
    ("09/25/2003", datetime(2003, 9, 25), "date with slash"),
    ("25/09/2003", datetime(2003, 9, 25), "date with slash"),
    ("10/09/2003", datetime(2003, 10, 9), "date with slash"),
    ("10/09/03", datetime(2003, 10, 9), "date with slash"),
    ("2003 09 25", datetime(2003, 9, 25), "date with space"),
    ("09 25 2003", datetime(2003, 9, 25), "date with space"),
    ("25 09 2003", datetime(2003, 9, 25), "date with space"),
    ("10 09 2003", datetime(2003, 10, 9), "date with space"),
    ("10 09 03", datetime(2003, 10, 9), "date with space"),
    ("25 09 03", datetime(2003, 9, 25), "date with space"),
    ("03 25 Sep", datetime(2003, 9, 25), "strangely ordered date"),
    ("25 03 Sep", datetime(2025, 9, 3), "strangely ordered date"),
    ("  July   4 ,  1976   12:01:02   am  ", datetime(1976, 7, 4, 0, 1, 2), "extra space"),     #[]
    ("Wed, July 10, '96", datetime(1996, 7, 10, 0, 0), "random format"),        #[]
    ("1996.July.10 AD 12:08 PM", datetime(1996, 7, 10, 12, 8), "random format"),    #[(1996, 7, 10),(1996, 7, 10)]
    ("July 4, 1976", datetime(1976, 7, 4), "random format"),
    ("7 4 1976", datetime(1976, 7, 4), "random format"),
    ("4 jul 1976", datetime(1976, 7, 4), "random format"),
    ("4 Jul 1976", datetime(1976, 7, 4), "'%-d %b %Y' format"),
    ("7-4-76", datetime(1976, 7, 4), "random format"),
    ("19760704", datetime(1976, 7, 4), "random format"),
    ("0:01:02 on July 4, 1976", datetime(1976, 7, 4, 0, 1, 2), "random format"),
    ("July 4, 1976 12:01:02 am", datetime(1976, 7, 4, 0, 1, 2), "random format"),
    ("Mon Jan  2 04:24:27 1995", datetime(1995, 1, 2, 4, 24, 27), "random format"),
    ("04.04.95 00:22", datetime(1995, 4, 4, 0, 22), "random format"),
    ("Jan 1 1999 11:23:34.578", datetime(1999, 1, 1, 11, 23, 34, 578000), "random format"),
    ("950404 122212", datetime(1995, 4, 4, 12, 22, 12), "random format"),
    ("3rd of May 2001", datetime(2001, 5, 3), "random format"),
    ("5th of March 2001", datetime(2001, 3, 5), "random format"),
    ("1st of May 2003", datetime(2003, 5, 1), "random format"),
    ('0099-01-01T00:00:00', datetime(99, 1, 1, 0, 0), "99 ad"),
    ('0031-01-01T00:00:00', datetime(31, 1, 1, 0, 0), "31 ad"),
    ("20080227T21:26:01.123456789", datetime(2008, 2, 27, 21, 26, 1, 123456), "high precision seconds"),
    ('13NOV2017', datetime(2017, 11, 13), "dBY (See GH360)"),
    ('0003-03-04', datetime(3, 3, 4), "pre 12 year same month (See GH PR #293)"),
    ('December.0031.30', datetime(31, 12, 30), "BYd corner case (GH#687)"),

    # Cases with legacy h/m/s format, candidates for deprecation (GH#886)
    ("2016-12-21 04.2h", datetime(2016, 12, 21, 4, 12), "Fractional Hours"),
]

    def test_SingleDate(self):    
        self.assertEqual(de.DateParse('09-feb-21')[0],                 [date(2021, 2, 9)])
        self.assertEqual(de.DateParse('09.07.1999')[0],                [date(1999, 9, 7)])
        self.assertEqual(de.DateParse('20 jan 2021')[0],               [date(2021, 1,20)])
        self.assertEqual(de.DateParse('18 oct 19')[0],                 [date(2019, 10,18)])

        self.assertEqual(de.DateParse('January 19, 2021')[0],          [date(2021, 1,19)])
        self.assertEqual(de.DateParse('Jan 29, 21')[0],                [date(2021, 1,29)])
        self.assertEqual(de.DateParse('Jan 29, 2022')[0],              [date(2022, 1,29)])
        self.assertEqual(de.DateParse('2023, February 21')[0],         [date(2023, 2,21)])

        self.assertEqual(de.DateParse('21/Jan/2021')[0],               [date(2021, 1,21)])
        self.assertEqual(de.DateParse('09-jan-2021')[0],               [date(2021, 1, 9)])
        self.assertEqual(de.DateParse('09-jan-21')[0],                 [date(2021, 1, 9)])
        self.assertEqual(de.DateParse('29 Jan \'21')[0],               [date(2021, 1,29)])
        self.assertEqual(de.DateParse('29 Jan, 2019')[0],              [date(2019, 1,29)])
        self.assertEqual(de.DateParse('29 January 2021')[0],           [date(2021, 1, 29)])
    
        self.assertEqual(de.DateParse('2021-01-30')[0],                [date(2021,1,30)])

    def test_TwoDates(self):
        self.assertEqual(de.DateParse('09.07.2001\n09-feb-21')[0],     [date(2001,9,7), date(2021, 2,9)])
        self.assertEqual(de.DateParse('09.07.2002 09-feb-21')[0],      [date(2002,9,7), date(2021, 2,9)])
        self.assertEqual(de.DateParse('09.07.2002 09 feb 2021')[0],    [date(2002,9,7), date(2021, 2,9)])
        self.assertEqual(de.DateParse('09 07 2002, 09 feb 2021')[0],   [date(2002,9,7), date(2021, 2,9)])

    def test_ParserDates(self):
        for el in self.PARSER_TEST_CASES:
            pred = de.DateParse(el[0])
            self.assertEqual((pred[0] + pred[1]), [el[1].date()])


                
if __name__ == '__main__':
    unittest.main() 
