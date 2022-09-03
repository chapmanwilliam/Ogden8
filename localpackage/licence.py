import pygsheets
from localpackage.mymain import spreadsheet_DigitalGoods
import datetime

def check_in_list(unique_code):
    #returns true if unique code in list
    #get list
    gc = pygsheets.authorize(service_file=service_file_path)
    shDigitalGoods = gc.open_by_key(spreadsheet_DigitalGoods)
    wks=shDigitalGoods.worksheet_by_title('Codes')
    codes = [wks.get_col(2,include_tailing_empty=False),wks.get_col(4,include_tailing_empty=False),wks.get_col(6,include_tailing_empty=False)] #the three codes
    for code in codes:
        if unique_code in code:
            ro=code.index(unique_code)
            uses=wks.get_value((ro+1,3))
            if uses=="":
                #unactivated - so add date
                wks.update_value((ro+1,3),datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
            else : #can only use token 3 times
                n=datetime.today()
                a=datetime.strptime(uses,'%Y-%m-%d %H:%M:%S')
                e=add_years(a,1)
                if n<=e:
                    return True
    return False

def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (datetime(d.year + years, 1, 1) - datetime(d.year, 1, 1))