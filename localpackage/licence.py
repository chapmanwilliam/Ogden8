import pygsheets
from localpackage.mymain import spreadsheet_DigitalGoods


def check_in_list(unique_code):
    #returns true if unique code in list
    #get list
    gc = pygsheets.authorize(service_file=service_file_path)
    shDigitalGoods = gc.open_by_key(spreadsheet_DigitalGoods)
    wks=shDigitalGoods.worksheet_by_title('Codes')
    x = wks.get_col(2,include_tailing_empty=False)
    if unique_code in x:
        r=x.index(unique_code)
        uses=int(wks.get_value((r+1,3)))
        uses+=1
        wks.update_value((r+1,3),uses)
        if uses<4: #can only use token 3 times
            return True
    return False