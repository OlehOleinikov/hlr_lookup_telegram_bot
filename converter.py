from config import LIST_LIMIT
from logger import logger

"""Char sets for subscribers split"""
chars_to_remove = ['-', '(', ')', '+', ]
chars_delimiter = ['\t', '\n', ';', ',', ' ']


def message_to_subscribers_list(string_text) -> list:
    """Split user message by phone numbers. Returns list of strings"""
    for separator_num in range(len(chars_delimiter)-1):
        string_text = string_text.replace(chars_delimiter[separator_num+1], chars_delimiter[0])
    for char_num in range(len(chars_to_remove)):
        string_text = string_text.replace(chars_to_remove[char_num], '')
    number_list = string_text.split(chars_delimiter[0], maxsplit=-1)
    clear_number_list = []
    for number in number_list:
        number = check_number(number)
        if 10 < len(number) < 15:
            clear_number_list.append(str(number))
    clear_number_list = list(set(clear_number_list))
    if len(clear_number_list) > LIST_LIMIT:
        clear_number_list = clear_number_list[:LIST_LIMIT]
        logger.warning(f'More than list limit recieved - {len(clear_number_list)}')
    return clear_number_list


def check_number(s):
    """
    Reformat and clean single phone number
    This case - Ukrainian locale, other country codes leave without changes.
    """
    s = str(s)
    if s.endswith('.0'):
        s = s[:-2]
    if s.startswith('C') and s.endswith('FT'):
        s = s[1:-2]
    if s.startswith('959000') and len(s) > 15:
        s = s[6:]
    if s.startswith('005380') and len(s) == 15:
        s = s[3:]
    if s.startswith('mms.+'):
        s = s[5:]
    if s.startswith('mms.') and len(s) > 5 and s[4].isdigit():
        s = s[4:]
    if s.startswith('380') and len(s) > 12 and s[12] == 'L':
        s = s[:12]
    if s.startswith('U380') and len(s) == 13:
        s = s[1:]
    if s.startswith('U0') and len(s) == 11:
        s = '38' + s[1:]
    if s.startswith('0380') and len(s) == 13:
        s = s[1:]
    if s.isdigit() and len(s) == 9:
        a = "380" + s
    elif s.isdigit() and len(s) == 10 and s.startswith("0"):
        a = "38" + s
    elif s.isdigit() and len(s) == 11 and s.startswith("80"):
        a = "3" + s
    elif s.isdigit() and len(s) == 15 and (s.startswith("810380") or s.startswith("818380")):
        a = s[-12:]
    elif s.isdigit() and len(s) == 7 and s.startswith('000010'):
        a = s[4:]
    else:
        a = s
    if not s.isdigit():
        a = ''
    return a

