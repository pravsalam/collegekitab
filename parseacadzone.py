#this file parses acadzone website to get book list for each branch
from bs4 import BeautifulSoup
from bs4 import BeautifulStoneSoup
import urllib2
import  xlwt
#universities
universities = {'Vishveswaraiah Technological University':['visvesvaraya Tech Univ','VTU'],
                'Anna University':['Anna University','ANNA']}
#branch codes
branch_code = {'B E Computer Science and Engineering':['Computer Science','CS','Engineering'],
               'B E Civil Engineering':['Civil Engineering','CE','Engineering'],
               'B E Electrical and Electronics Engineering':['Electrical & Electronics','EEE','Engineering'],
               'B E Electronics and Communication Engineering':['Electronics & Comm.','ECE','Engineering'],
               'B E Mechanical Engineering':['Mechanical Engineering','ME','Engineering'],
               'B Tech (Chemical Engineering)':['Chemical Engineering','CHE','Engineering'],
               'B Tech (Information Technology)':['Information Tech','IT','Engineering'],
               'B Tech (Civil Engineering)':['Civil Engineering','CE','Engineering'],
               'B Tech (Computer Science And Engineering)':['Computer Science','CS','Engineering'],
               'B Tech (Electrical And Electronics Engineering)':['Electrical & Electronics','EEE','Engineering'],
               'B Tech (Electronics And Communication Engineering)':['Electronics & Comm.','ECE','Engineering'],
               'B Tech (Information Science And Engineering)':['Information Tech','IT','Engineering'],
               'B Tech (Instrumentation Technology)':['Instrumentation','INS','Engineering'],
               'B Tech (Mechanical Engineering)':['Mechanical Engineering','ME','Engineering'],
               'B Tech (Telecommunication Engineering)':['Telecom Eng.','TEL','Engineering'],
               'B E Aeronautical Engineering':['Aeronautical Eng.','AER','Engineering'],
               'B Tech (Aeronautical Engineering)':['Aeronautical Eng.','AER','Engineering'],
               'B E Electronics And Instrumentation Engineering':['Electronics & Instr Eng.','EIE','Engineering'],
               'MBA':['MBA','MBA','MBA'],
               'B Arch':['B Arch','BARCH','Engineering']}

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
"""ws_books.write(0,0,"Serial Number")
ws_books.write(0,1,"University")
ws_books.write(0,2,"University Name")
ws_books.write(0,3,"Main Category")
ws_books.write(0,4,"Semester")
ws_books.write(0,5,"Subject")
ws_books.write(0,6,"Book Title")
ws_books.write(0,7,'Authors')
ws_books.write(0,8,"Publisher")
ws_books.write(0,9,"ISBN")
ws_books.write(0,10,"Branch Code")
ws_books.write(0,11,"University Code")
row_id+=1"""
url_file = open('url_list.txt','r')

for url in url_file:
    url = url.strip()
    print url
    website = urllib2.urlopen(url)
    web_html = website.read()
    soup = BeautifulSoup(web_html)
    body = soup.find('body')
    if not body:
        soup = BeautifulSoup(soup.prettify(formatter=None))
        body = soup.find('body')
    body_tag = body.find(id='body_container')
    college_tag = body_tag.find('div',id='breadcrumb')
    print college_tag
    university_name_tag = college_tag.find('div',attrs={'class':'link_type1'})
    univ_name = university_name_tag.get_text()
    university_info_list = universities.get(univ_name)
    university_name = university_info_list[0]
    university_code = university_info_list[1]
    book_info['university'] = university_name
    book_info['university_code'] = university_code
    #college_tag = college_tag.find_next('div',attrs={'class':'link_type1'})
    college_tag  = university_name_tag.find_next_sibling('div',attrs={'class':'link_type1'})
    college_name = college_tag.get_text()
    #branch_tag = college_tag.find_next('div',attrs={'class':'link_type1'})
    branch_tag = college_tag.find_next_sibling('div',attrs={'class':'link_type1'})
    branch_name = branch_tag.get_text()

    print branch_name
    if branch_name:
        branch_info_list = branch_code.get(branch_name)
        book_info['branch'] = branch_info_list[0]
        book_info['branch_code'] = branch_info_list[1]
        book_info['category'] = branch_info_list[2]
        
    sem_tag = branch_tag.find_next_sibling('div',attrs={'class':'link_type2'})
    sem = book_info['semester'] = sem_tag.get_text()
    print sem
    if sem == 'Semester 1' or sem =='Semester 2':
        book_info['branch'] ='Common Subjects'
        book_info['branch_code'] = 'COM'
        
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
            ws_books.write(row_id,1,"University")
            ws_books.write(row_id,2,book_info['university'])
            ws_books.write(row_id,3,book_info['category'])
            ws_books.write(row_id,4,book_info['branch'])
            ws_books.write(row_id,5,book_info['semester'])
            ws_books.write(row_id,6,book_info['subject'])
            ws_books.write(row_id,7,book_info['name'])
            ws_books.write(row_id,8,book_info['author'])
            ws_books.write(row_id,9,book_info['publisher'])
            ws_books.write(row_id,10,book_info['isbn'])
            ws_books.write(row_id,11,book_info['branch_code'])
            ws_books.write(row_id,12,book_info['university_code'])
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
            """ws_books.write(row_id,0,serial_number)
            ws_books.write(row_id,1,book_info['subject'])
            ws_books.write(row_id,2,book_info['name'])
            ws_books.write(row_id,3,book_info['author'])
            ws_books.write(row_id,4,book_info['publisher'])
            ws_books.write(row_id,5,book_info['isbn'])"""
            ws_books.write(row_id,0,serial_number)
            ws_books.write(row_id,1,"University")
            ws_books.write(row_id,2,book_info['university'])
            ws_books.write(row_id,3,book_info['category'])
            ws_books.write(row_id,4,book_info['branch'])
            ws_books.write(row_id,5,book_info['semester'])
            ws_books.write(row_id,6,book_info['subject'])
            ws_books.write(row_id,7,book_info['name'])
            ws_books.write(row_id,8,book_info['author'])
            ws_books.write(row_id,9,book_info['publisher'])
            ws_books.write(row_id,10,book_info['isbn'])
            ws_books.write(row_id,11,book_info['branch_code'])
            ws_books.write(row_id,12,book_info['university_code'])
            row_id+=1
            serial_number+=1
            file_name = "books_list"+".xls"
            wbk.save(file_name)
    book_info={}
url_file.close()
file_name = "books_list"+".xls"
wbk.save(file_name)
            
            
            