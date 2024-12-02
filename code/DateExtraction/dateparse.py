
from dateutil.parser import parse
from dateutil.parser._parser import ParserError
import re


likelyFormats = [ r'\d\d?(st|nd|rd|th) of (Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?) \d\d\d\d',
    
                r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s(\d\d?)\s(\d\d:\d\d:\d\d)\s\d\d\d\d',

                r'(?:\d{8})T(?:\d\d){1,3}',

                r'\d\d?((JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\d\d(?:\d\d)?)',

                r'(January|February|March|April|May|June|July|August|September|October|November|December)\.\d{4}\.\d{2}',
    
                r'(\d\d\d\d)([ \.\-/])(\d\d?)\2(\d\d?)',
              
                r'(\d\d?)([\s\.\-/])(\d\d?)\2(\d\d\d\d)',

                r'(\d\d\d\d)\,?([\s\.\-/])(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\2(\d\d)',

                r'(?<!\d\d)(\d\d?)([\s\.\-/])(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(((\2|(\,\s?))(\d\d){1,2})|(\s\'\d\d))',            

                r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)([\s\.\-/])(\d\d?)\s?\,?\2((\d\d){1,2}|(\'\d\d))',

                r'\b(\d\d)\s(\d\d)\s(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
]
speculativeFormats = [  r'\d\d?([\s\.\-/])\d\d?\1\d\d?',
                      
                        r'\b\d{8}\b|\b\d{12}\b|\b\d{14}\b',

                        r'\b(\d{6} \d{6})\b'
]


def CheckForDuplicates(already_found : list, match: str) -> bool:
    for date in already_found:
        if match in date:
            return False
    return True



compiledFormats = [list(map(lambda rex: re.compile(rex, re.IGNORECASE), likelyFormats)), 
                   list(map(lambda rex: re.compile(rex, re.IGNORECASE), speculativeFormats))]


def DateParse(tagContent : str) -> tuple :
    """Function for finding date patterns

    Args:
        tagContent (str): A string to be parsed in search of dates

    Returns:
        tuple: A tuple containing two lists: first one contains dates that are likely to be relevant,
            while the second one contains speculative dates, found using a broad definition of a date format
    """
    
    dates = [[],[]]
    already_found = []
    tagContent = re.sub(r'\s+', ' ', tagContent)
    for i in range(2):
        for format in compiledFormats[i]:
            if matches := format.finditer(tagContent):
                for match in matches:
                    if CheckForDuplicates(already_found, match[0]):
                        try:
                            dates[i] .append(parse(match[0]).date())
                            already_found.append(match[0])
                        except ParserError:
                            pass

    return (dates[0], dates[1])
