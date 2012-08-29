from xlrd import *
import xlwt
mba_branches =['Marketing','Common','Finance','IT','HR','Strategy','Operations']
branches_wbk = open_workbook('MBA branches.xls')
blist_wbk = open_workbook('booklist/mba_book_list.xls')
for mba_branch in mba_branches:
    wbk = xlwt.Workbook(encoding='UTF-8')
    ws_books = wbk.add_sheet('books')
    row = 0
    index = 1
    sub_sh = branches_wbk.sheet_by_index(0)
    for sub_rowno in range(sub_sh.nrows):
        sub_list = sub_sh.row_values(sub_rowno)
        subject = sub_list[0]
        branch = sub_list[1]
        if mba_branch == branch:
            books_sh = blist_wbk.sheet_by_index(0)
            for book_rowno in range(books_sh.nrows):
                book_list = books_sh.row_values(book_rowno)
                book_subject = book_list[1]
                book_info={}
                if book_subject == subject:
                    ws_books.write(row,0,index)
                    ws_books.write(row,1,'MBA')
                    ws_books.write(row,2,branch)
                    ws_books.write(row,3,book_subject)
                    ws_books.write(row,4,book_list[2])
                    ws_books.write(row,5,book_list[3])
                    ws_books.write(row,6,book_list[4])
                    ws_books.write(row,7,book_list[5])
                    ws_books.write(row,8,branch)
                    row+=1
                    index+=1
    file_name = 'booklist/mba_'+mba_branch+'_book_list.xls'
    wbk.save(file_name)
                    