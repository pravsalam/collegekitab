import xlwt3 as xlwt
wbk = xlwt.Workbook()
ws = wbk.add_sheet('Test sheet')
ws.write(0,0,)
wbk.save('what.xls')
print("success")