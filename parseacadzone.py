#this file parses acadzone website to get book list for each branch
from bs4 import BeautifulSoup
from urllib.request import urlopen
import xlwt3 as xlwt
import bottlenose

book_info={}
wbk = xlwt.Workbook()
ws_books = wbk.add_sheet('books')
#book_info[subject']
#book_info['name']
#book_info['author']
#book_info['publisher']
#book_info['isbn']
#write heading of the worksheet 
row_id=0
serial_number=1
ws_books.write(0,0,"Serial Number")
ws_books.write(0,1,"Subject")
ws_books.write(0,2,"Book Title")
ws_books.write(0,3,'Authors')
ws_books.write(0,4,"Publisher")
ws_books.write(0,5,"ISBN")
row_id+=1
url_file = open('url_list.txt','r')
for url in url_file:
    url = url.strip()
    website = urlopen(url)
    web_html = website.read()
    soup = BeautifulSoup(web_html)
    for subject_tag in soup.find_all('div',attrs={'class':'subject'}):
        #get subject name
        subject = subject_tag.find('h2').get_text()[12:]
        #print(subject)
        book_info['subject']=subject
        #get the title of the book
        books_for_subject_tag= subject_tag.find_next('div',attrs={'class':'books'})
        for book_list_tag in books_for_subject_tag.find_all('div',attrs={'class':'booksouter'}):
            isbn =dict(book_list_tag.attrs).get('onmouseover').split("'")[1].split('_')[1]
            #print(isbn)
            book_info['isbn']=isbn
            book_title_tag = book_list_tag.find('div',attrs={'class':'col3'})
            list_book_dets=[]
            for book_dets_tag in book_title_tag.find_all('div'):
                list_book_dets.append(book_dets_tag.get_text())
            book_info['name'] = list_book_dets[0]
            book_info['author'] = list_book_dets[1].split(':')[1]
            book_info['publisher']= list_book_dets[2].split(':')[1]
            print(book_info)
            ws_books.write(row_id,0,serial_number)
            ws_books.write(row_id,0)
            ws_books.write(row_id,1,book_info['subject'])
            ws_books.write(row_id,2,book_info['name'])
            ws_books.write(row_id,3,book_info['author'])
            ws_books.write(row_id,4,book_info['publisher'])
            ws_books.write(row_id,5,book_info['isbn'])
            row_id+=1
            serial_number+=1
        reference_book_tag = books_for_subject_tag.find_next('div',attrs={'class':'books'})
        for ref_book_list_tag in reference_book_tag.find_all('div',attrs={'class':'booksouter'}):
            isbn= dict(ref_book_list_tag.attrs).get('onmouseover').split("'")[1].split('_')[1]
            book_info['isbn'] = isbn
            book_title_tag = ref_book_list_tag.find('div',attrs={'class':'col3'})
            list_book_dets=[]
            for book_dets_tag in book_title_tag.find_all('div'):
                list_book_dets.append(book_dets_tag.get_text())
            book_info['name'] = list_book_dets[0]
            book_info['author'] = list_book_dets[1].split(':')[1]
            book_info['publisher']= list_book_dets[2].split(':')[1]
            print(book_info)
            ws_books.write(row_id,0,serial_number)
            ws_books.write(row_id,1,book_info['subject'])
            ws_books.write(row_id,2,book_info['name'])
            ws_books.write(row_id,3,book_info['author'])
            ws_books.write(row_id,4,book_info['publisher'])
            ws_books.write(row_id,5,book_info['isbn'])
            row_id+=1
            serial_number+=1
    book_info={}
url_file.close()        
wbk.save('book_list.xls')
            
            
            