from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,Text
from sqlalchemy import Sequence,Table
from sqlalchemy.orm import sessionmaker,relationship, backref
from sqlalchemy import ForeignKey
import datetime as dt
import logging
import xlrd
import xlutils
import shutil
import beautifulSoup as bs
import write_to_sql_files as wsql
cat_count =1
prod_count = 1
#open workbook
#wb = xlrd.open_workbook('booklist/eng_cse_compsc_book_list.xls')
#sh = wb.sheet_by_index(0)
#end of open workbook
engine = create_engine('sqlite:///cknew.db')
Base = declarative_base()
logging.basicConfig(file='db_populate.log',level=logging.DEBUG)
#define associate table between books and related books
related_books_assoc = Table('related_books',Base.metadata,
                            Column('book_id',Integer,ForeignKey('Books.book_id')),
                            Column('related_book_id',Integer,ForeignKey('RelatedBooks.related_book_id')))
subjects_books_assoc = Table('Subject_books',Base.metadata,
                             Column('subject_id',Integer,ForeignKey('Subjects.subject_id')),
                             Column('book_id',Integer,ForeignKey('Books.book_id')))
branches_books_assoc = Table ('Branch_books',Base.metadata,
                              Column('branch_id',Integer,ForeignKey('Branches.branch_id')),
                              Column('book_id',Integer,ForeignKey('Books.book_id')))
#define classes and relations
class MainMenu(Base):
    __tablename__ = 'MainMenu'
    name= Column(String(length=50),nullable = False)
    menu_id  = Column(Integer,Sequence('menu_id_seq',start =1 ),primary_key=True)
    sort_order = Column(Integer,Sequence('sort_order_seq',start=1))
    time_entry = Column(String)#dt.datetime.now().strftime("%Y-%d-%d %H:%M:%S")
    time_mod  = Column(String)
    #braches = relationship('Branches',order_by = 'Branches.branch_id',backref ='Branches')
    def __init__(self,name='None'):
        global cat_count
        self.menu_id=cat_count
        self.name=name
        self.time_entry = dt.datetime.now().strftime("%Y-%d-%d %H:%M:%S")
        self.time_mod = dt.datetime.now().strftime("%Y-%d-%d %H:%M:%S")
        cat_count+=1
    def __repr__(self):
        return "Menu < '%s'>" %(self.name)
class Universities(Base):
    __tablename__ = 'Universities'
    univ_name = Column(String(length=100),nullable = False)
    univ_id = Column(Integer,primary_key = True)
    parent_menu_id = Column(Integer,ForeignKey(MainMenu.menu_id))
    main_cat= relationship('MainMenu',backref = backref('universities',order_by=univ_id))
    def __init__(self,university_name):
        global cat_count
        self.univ_name = university_name
        self.univ_id = cat_count
        cat_count+=1
    def __repr__(self):
        return "university Name <'%s'>" %(self.univ_name)
    
class UnivBranches (Base):
    __tablename__ = 'UnivBranches'
    univbra_name = Column(String(length=100),nullable=False)
    univbra_real_name = Column(String(length=100),nullable=False)
    univbra_id = Column(Integer,primary_key =True)
    parent_univ_id = Column(Integer,ForeignKey(Universities.univ_id))
    university = relationship('Universities',backref = backref('univbranches',order_by=univbra_id))
    def __init__(self,univbranch_name,univbranch_real_name):
        global cat_count 
        self.univbra_name = univbranch_name
        self.univbra_id = cat_count
        self.univbra_real_name = univbranch_real_name
        cat_count+=1
    def __repr__(self):
        return "university branch <'%s'>" %(self.univbra_name)
        
class Branches(Base):
    __tablename__ = 'Branches'
    branch_name = Column(String(length=50),nullable = False)
    branch_id = Column(Integer,Sequence('branch_id_seq',start = 50,increment=1),primary_key = True)    
    parent_menu_id = Column(Integer,ForeignKey(MainMenu.menu_id))
    sort_order = Column(Integer)
    time_entry = Column(String)
    time_mod = Column(String)
    main_cat = relationship('MainMenu',backref = backref('branches',order_by=branch_id))
    branch_books = relationship(('Books'),secondary=branches_books_assoc,backref='parent_branches')
    #subjects = relationship('Subjects',order_by = 'Subjects.subject_id',backref = 'Subjects.parent_branch')
    def __init__(self,name):
        global cat_count
        self.branch_id = cat_count
        self.branch_name = name
        self.time_enty = dt.datetime.now().strftime("%Y-%d-%d %H:%M:%S")
        self.time_mod = dt.datetime.now().strftime("%Y-%d-%d %H:%M:%S")
        cat_count+=1
    def __repr__(self):
        return "Branch Name <'%s'>" %(self.branch_name)
#subjects table 
class Subjects(Base):
    __tablename__ = 'Subjects'
    subject_name = Column(String(length=200),nullable = False)
    subject_real_name = Column(String(length = 250))
    subject_id = Column(Integer, Sequence('subject_id_seq',start=1000,increment=1),primary_key = True )
    parent_branch_id = Column(Integer, ForeignKey(UnivBranches.univbra_id))
    sort_order = Column(Integer)
    time_entry = Column(String)
    time_mod = Column(String)
    parent_branch = relationship('UnivBranches',backref = backref('subjects',order_by=subject_id))
    subject_books = relationship('Books',secondary=subjects_books_assoc,backref='parent_subjects')
    #books =  relationship('Books',order_by = 'Books.book_id',backref = 'Books.subject')
    def __init__(self,name,realname=''):
        global cat_count
        self.subject_id = cat_count
        self.subject_name = name
        if realname == '':
            self.subject_real_name=name
        else:
            self.subject_real_name = realname
        self.sort_order = 0
        self.time_entry = dt.datetime.now().strftime("%Y-%d-%d %H:%M:%S")
        self.time_mod = dt.datetime.now().strftime("%Y-%d-%d %H:%M:%S")
        cat_count+=1
    def __repr__(self):
        return "Subject Name <'%s'>" %(self.subject_name)
        
class Books(Base):
    __tablename__ = 'Books'
    book_name_author = Column(String,nullable=False)
    book_id = Column(Integer,Sequence('book_id_seq',start=1),primary_key =True)
    #parent_subject_id = Column(Integer,ForeignKey(Subjects.subject_id))
    book_author = Column(String)
    book_publisher = Column(String)
    book_edition = Column(String)
    book_publish_date= Column(String)
    book_pages = Column(Integer)
    book_price = Column(Integer)
    book_special_price  = Column(Integer)
    book_points = Column(Integer)
    book_points_earned = Column(Integer)
    #book_price_reduced = Column(Integer)
    book_price_reduced_used = Column(Integer)
    book_points_reduced_used = Column(Integer)
    book_isbn10 = Column(Integer)
    book_isbn13 = Column(Integer)
    book_seo_keyword  = Column(String)
    book_meta_desc= Column(Text)
    book_meta_keyword = Column(Text)
    book_desc = Column(Text)
    book_image = Column(String)
    #subject = relationship('Subjects',backref =backref('books', order_by = book_id))
    related_books = relationship('RelatedBooks',secondary =related_books_assoc,backref='parent_books')
    #relatedbook_id = relationship('RelatedBooks',order_by='RelatedBooks.related_bookid',backref='Relatedbooks.parent_bookid')
    def __init__(self,book_info_dict):
        #book info dictionary 
        #book_info['prod_id']
        #book_info['name']
        #book_info[image_name']
        #book_info['price']
        #book_info['points']
        #book_info['seo_key_word']
        #book_info['description']
        #book_info['meta_desc']
        #book_info['meta_keywords']
        #book_info['additional_img']
        #book_info['price_reduced_on_used']
        #book_info['point_reduced_on_used']
        #book_info['authors']
        #book_info['publisher']
        #book_info['year_edition']
        #book_info['edition']
        #book_info['special_price']
        #book_info['points_earned']
        #book_info['isbn10']
        #book_info['isbn13']
        #book_info['pages']
        global prod_count
        self.book_id = prod_count
        prod_count+=1
        if 'name' in book_info_dict:
            self.book_name_author = book_info_dict['name']
        if 'authors' in book_info_dict:
            self.book_author = book_info_dict['authors']
        if 'publisher' in book_info_dict:
            self.book_publisher = book_info_dict['publisher']
        if 'edition' in book_info_dict:
            self.book_edition = book_info_dict['edition']
        if 'year_edition' in book_info_dict:
            self.book_publish_date = book_info_dict['year_edition']
        if 'pages' in book_info_dict:
            self.book_pages = book_info_dict['pages']
        if 'price' in book_info_dict:
            self.book_price = book_info_dict['price']
        if 'special_price' in book_info_dict:
            our_price = book_info_dict['special_price']
            self.book_special_price = our_price
            self.book_points = int(our_price)*4
            self.book_points_earned = int(our_price)/10
        if 'price_reduced_on_used' in book_info_dict:
            self.book_price_reduced_used = book_info_dict['price_reduced_on_used']
            self.book_points_reduced_used = int(book_info_dict['price_reduced_on_used'])/10
        if 'seo_key_word' in book_info_dict:
            self.book_seo_keyword = book_info_dict['seo_key_word']
        if 'meta_desc' in book_info_dict:
            self.book_meta_desc = book_info_dict['meta_desc']
        if 'description' in book_info_dict:
            self.book_desc = unicode(book_info_dict['description'])
        if 'meta_keywords' in book_info_dict:
            self.book_meta_keyword =  book_info_dict['meta_keywords']
        if 'isbn10' in book_info_dict:
            self.book_isbn10 = book_info_dict['isbn10']
        if 'isbn13' in book_info_dict:
            self.book_isbn13 = book_info_dict['isbn13']
        if 'image' in book_info_dict:
            self.book_image = book_info_dict['image']
    def __repr__(self):
        return "Book <Name ='%s', isbn ='%d' >"%(self.book_name_author,self.book_isbn13)
class RelatedBooks(Base):
    __tablename__ = 'RelatedBooks'
    related_book_id = Column(Integer,primary_key=True)
    #parent_book = relationship('Books',backref=backref('related_books',order_by =related_book_id))
    def __init__(self,book_id):
        self.related_book_id = book_id
    def __repr__(self):
        return "'%d'" %(self.related_book_id)
#execute the command to create     all tables
Base.metadata.create_all(engine)
#create session object
session = sessionmaker(bind=engine)()
# calculate next cat id 
cat_count+=len(session.query(MainMenu).all())
cat_count+=len(session.query(Universities).all())
cat_count+=len(session.query(UnivBranches).all())
cat_count+=len(session.query(Branches).all())
cat_count+=len(session.query(Subjects).all())
prod_count+=len(session.query(Books).all())
print cat_count
print prod_count


#testing workbook
def populate_db():
    excel_files=['eng_ece_book_list.xls','eng_eee_book_list.xls','eng_instrument_book_list.xls','eng_ise_book_list.xls','eng_mech_book_list.xls','eng_telecom_book_list.xls']
    for excel_file in excel_files:
        excel_file = 'booklist/'+excel_file
        wb = xlrd.open_workbook(excel_file)
        sh = wb.sheet_by_index(0)
        for rownum in range(sh.nrows):
            row_list = sh.row_values(rownum)
            """ get ISBN search for it, if it does not existing ask out beautifulSoup program to get
            get informatiom in a dictionary. then initiate the book. search for subject, if it exist add to it
            if it does not exist create a subject. Search for branch if it exist add subject to branch, else create branch.
            if Main menu exist add branch to it. Now get the product id and insert into book_info dictionary, call workbook
            writing function to write to workbook"""
            
            #print book_info
            isbn_str = row_list[9]
            isbn_int= int(row_list[9])
            branch_str = row_list[4]
            sub_str = row_list[5]
            univ_str = row_list[2]
            univ_code= row_list[11]
            first_catstr = row_list[1]
            scnd_catstr = row_list[3]
            branch_code = row_list[10]
            print isbn_str
            check_book = session.query(Books).filter_by(book_isbn13=isbn_int).first()
            if not check_book:
                print "book is not there"
                book_info = bs.populate_book_info_fp(isbn_str)
                if not book_info:
                    book_info = bs.populate_book_info_bookadda(isbn_str)
                if not book_info:
                    book_info = bs.populate_book_info_uread(isbn_str)
                if not book_info:
                    continue
                if not bs.download_prod_img(isbn_str):
                    logging.info('unable to download image for isbn %s',isbn_str)
                    destin_img='isbn/noimage_cklogo_'+isbn_str+'.jpg'
                    shutil.copy2('cklogo.jpg',destin_img)
                check_book  = Books(book_info)
            else:
                print "book exists already"
                pass
            subject_real_str_name = sub_str.strip()+'_'+branch_code+'_'+univ_code
            print subject_real_str_name
            #check if the subject exist
            check_subject=session.query(Subjects).filter_by(subject_real_name =subject_real_str_name).first()
            print check_subject
            if check_subject:
                #subject exist add to that 
                check_subject.subject_books.append(check_book)
                session.add(check_book)
                #session.commit()   
            else:
                print "subject %s does not exit, creating it" %(sub_str)
                new_subject = Subjects(name=sub_str,realname=subject_real_str_name)
                new_subject.subject_books.append(check_book)
                session.add(new_subject)
                print(branch_str)
                branch_real_name = branch_str+'_'+univ_code
                check_univbranch = session.query(UnivBranches).filter_by(univbra_real_name = branch_real_name).first()
                #print check_univbranch
                if check_univbranch:
                    check_univbranch.subjects.append(new_subject)
                    #session.add(new_subject)
                    #session.commit()
                    print check_univbranch.subjects   
                else:
                    print 'univbranch does not exist'
                    new_branch = UnivBranches(univbranch_name=branch_str,univbranch_real_name=branch_real_name)
                    new_branch.subjects.append(new_subject)
                    session.add(new_branch)
                    check_univ = session.query(Universities).filter_by(univ_name = univ_str).first()
                    if check_univ:
                        check_univ.univbranches.append(new_branch)
                        session.add(new_branch)
                    else:
                        print 'university does not exist'
                        print univ_str
                        new_univ = Universities(university_name = univ_str)
                        new_univ.univbranches.append(new_branch)
                        session.add(new_univ)
                        print first_catstr
                        check_cat = session.query(MainMenu).filter_by(name = first_catstr).first()
                        if check_cat:
                            check_cat.universities.append(new_univ)
                            #session.add(new_branch)
                            #session.commit()
                        else:
                            print 'main category does not exist'
                            new_cat = MainMenu(name=first_catstr)
                            new_cat.universities.append(new_univ)
                            session.add(new_cat)
                            session.commit()
                check_gen_branch = session.query(Branches).filter_by(branch_name=branch_str).first()
                if check_gen_branch:
                    print 'General Branch exists'
                    check_gen_branch.branch_books.append(check_book)
                else:
                    print 'General Branch does not exist Creating it' 
                    gen_branch = Branches(name=branch_str)
                    gen_branch.branch_books.append(check_book)
                    session.add(gen_branch)
                    check_sec_cat = session.query(MainMenu).filter_by(name = scnd_catstr).first()
                    if check_sec_cat:
                        print 'Second category exist'
                        check_sec_cat.branches.append(gen_branch)
                    else:
                        sec_cat = MainMenu(name=scnd_catstr)
                        session.add(sec_cat)
                        sec_cat.branches.append(gen_branch)  
            session.commit()
#dictionary to pass to write work book
def write_to_excel_file():
# reiterate database to find related books.
    for book_row in session.query(Books).all():
        print book_row.book_id
        b_dict = {}
        b_dict['prod_id'] = book_row.book_id
        b_dict['name'] = book_row.book_name_author
        b_dict['publisher'] = book_row.book_publisher
        b_dict['edition'] = book_row.book_edition
        b_dict['authors'] = book_row.book_author
        b_dict['year_edition'] = book_row.book_publish_date
        b_dict['pages'] = book_row.book_pages
        b_dict['price'] = book_row.book_price
        b_dict['special_price'] = book_row.book_special_price
        b_dict['points'] = book_row.book_points
        b_dict['points_earned'] = book_row.book_points_earned
        b_dict['price_reduced_on_used'] = book_row.book_price_reduced_used
        b_dict['points_reduced_on_used'] = book_row.book_points_reduced_used
        b_dict['isbn10'] = str(book_row.book_isbn10)
        b_dict['isbn13'] = str(book_row.book_isbn13)
        b_dict['seo_key_word'] = book_row.book_seo_keyword
        b_dict['meta_desc'] = book_row.book_meta_desc
        b_dict['meta_keywords'] = book_row.book_meta_keyword
        b_dict['description'] = book_row.book_desc
        b_dict['image'] = 'data/isbn/image_'+str(book_row.book_isbn13)+'.jpg'
        parent_cats =[]
        related_books_list = []
        for parent_subject in book_row.parent_subjects:
            b_dict['model'] = parent_subject.subject_name
            if not parent_subject.subject_id in parent_cats: 
                parent_cats.append(parent_subject.subject_id)
            else:
                pass
            if not parent_subject.parent_branch_id in parent_cats: 
                parent_cats.append(parent_subject.parent_branch_id)
            else:
                pass
            parent_branch = session.query(UnivBranches).filter_by(univbra_id = parent_subject.parent_branch_id).first()
            if not parent_branch.parent_univ_id in parent_cats: 
                parent_cats.append(parent_branch.parent_univ_id)
            else:
                pass
            parent_univ = session.query(Universities).filter_by(univ_id = parent_branch.parent_univ_id).first()
            if not parent_univ.parent_menu_id in parent_cats:
                parent_cats.append(parent_univ.parent_menu_id) 
        for gen_branch in book_row.parent_branches:
            print gen_branch.branch_name
            if not gen_branch.branch_id in parent_cats: 
                parent_cats.append(gen_branch.branch_id)
            if not gen_branch.parent_menu_id in parent_cats:
                parent_cats.append(gen_branch.parent_menu_id)
          
            cat_string = ','.join(str(num) for num in parent_cats)
            b_dict['parent_cats'] = cat_string
            
            """ for subject_book in  parent_subject.subject_books:
                if book_row.book_id != subject_book.book_id:
                    if not subject_book.book_id in related_books_list:
                        related_books_list.append(subject_book.book_id)"""
        for parent_sub in book_row.parent_subjects:
            for subject_book in parent_sub.subject_books:
                if book_row.book_id != subject_book:
                    if not subject_book.book_id in related_books_list:
                        related_books_list.append(subject_book.book_id)
                  
        print 'for book id  %d parent str is %s' %(book_row.book_id,cat_string)
        #print related_books_list            
        related_book_str = ','.join(str(num) for num in related_books_list)    
        print 'for book id %d related books are %s' %(book_row.book_id,related_book_str)
        b_dict['parent_cats'] = cat_string
        b_dict['related_books'] = related_book_str
        bs.write_to_prod_sheet(b_dict)
        bs.write_to_attrs_sheet(b_dict)
        bs.write_to_options_sheet(b_dict)
        bs.write_to_rewards_sheet(b_dict)
        bs.write_to_specials_sheet(b_dict)
        #wsql.write_prods_sql(b_dict)
        #wsql.write_prod_desc_sql(b_dict)
        #wsql.write_prod_attrs_sql(b_dict)
        #isbn = str(book_row.book_isbn13)
        
    #bs.save_wb()
    sort_order = 0 
    for menu in session.query(MainMenu).all():
        cat_info={}
        cat_info['cat_id'] = menu.menu_id
        cat_info['parent_cat'] = 0
        cat_info['cat_name'] = menu.name
        cat_info['q_isit_top'] = 'true'
        cat_info['sort_order'] = sort_order
        seo_list = menu.name.split()
        seo_string = '_'.join(str(key_word) for key_word in seo_list)
        seo_string = seo_string+'_'+'Books'
        cat_info['seo_key_words'] = seo_string
        meta_desc = ' buy ' +menu.name+ ' books online at collegekitab.com'
        meta_desc = meta_desc+ ' Collegekitab.com exclusively dedicated for academic books is favorite among students.'
        meta_desc = meta_desc+ ' at collegekitab.com you can not only buy books online, you can also buy used books or rent books on short term'
        meta_desc = meta_desc+ ' collegekitab.com is one stop shop for all engineering branches, MBA, medicine, arts and science books'
        cat_info['meta_desc'] = meta_desc
        cat_info['meta_keywords'] = meta_desc
        sort_order+=1
        bs.write_to_cats_sheet(cat_info)
    sort_order = 0
    for branch in session.query(Branches).all():
        cat_info={}
        cat_info['cat_id']= branch.branch_id
        cat_info['parent_cat'] = branch.parent_menu_id
        cat_info['cat_name'] = branch.branch_name
        cat_info['q_isit_top'] = 'false'
        cat_info['sort_order'] = sort_order
        seo_list = branch.branch_name.split()
        seo_string = '_'.join(str(key_word) for key_word in seo_list)
        seo_string = seo_string+'_'+'Books'
        cat_info['seo_key_words'] = seo_string
        meta_desc = ' buy ' +branch.branch_name+ ' books online at collegekitab.com'
        meta_desc = meta_desc+ ' Collegekitab.com exclusively dedicated for academic books is favorite among students.'
        meta_desc = meta_desc+ ' at collegekitab.com you can not only buy books online, you can also buy used books or rent books on short term'
        meta_desc = meta_desc+ ' collegekitab.com is one stop shop for all engineering branches, MBA, medicine, arts and science books'
        cat_info['meta_desc'] = meta_desc
        cat_info['meta_keywords'] = meta_desc
        sort_order+=1
        bs.write_to_cats_sheet(cat_info)
    sort_order = 0 
    for university in session.query(Universities).all():
        cat_info['cat_id'] = university.univ_id
        cat_info['parent_cat'] = university.parent_menu_id
        cat_info['cat_name'] = university.univ_name
        cat_info['q_isit_top'] = 'false'
        cat_info['sort_order'] = sort_order
        seo_list = university.univ_name.split()
        seo_string = '_'.join(str(key_word) for key_word in seo_list)
        seo_string = seo_string+' '+'Books'
        cat_info['seo_key_words'] = seo_string
        meta_desc = ' buy ' +university.univ_name+ ' books online at collegekitab.com'
        meta_desc = meta_desc+ ' Collegekitab.com exclusively dedicated for academic books is favorite among students.'
        meta_desc = meta_desc+ ' at collegekitab.com you can not only buy books online, you can also buy used books or rent books on short term'
        meta_desc = meta_desc+ ' collegekitab.com is one stop shop for all engineering branches, MBA, medicine, arts and science books'
        cat_info['meta_desc'] = meta_desc
        cat_info['meta_keywords'] = meta_desc
        sort_order+=1
        bs.write_to_cats_sheet(cat_info)
    sort_order = 0
    for univbranch in session.query(UnivBranches).all():
        cat_info['cat_id'] = univbranch.univbra_id
        cat_info['parent_cat'] = univbranch.parent_univ_id
        cat_info['cat_name'] = univbranch.univbra_name
        cat_info['q_isit_top'] = 'false'
        cat_info['sort_order'] = sort_order
        seo_list = univbranch.univbra_name.split()
        seo_string = '_'.join(str(key_word) for key_word in seo_list)
        seo_string = seo_string+' '+'Books'
        cat_info['seo_key_words'] = seo_string
        meta_desc = ' buy ' +univbranch.univbra_name+ ' books online at collegekitab.com'
        meta_desc = meta_desc+ ' Collegekitab.com exclusively dedicated for academic books is favorite among students.'
        meta_desc = meta_desc+ ' at collegekitab.com you can not only buy books online, you can also buy used books or rent books on short term'
        meta_desc = meta_desc+ ' collegekitab.com is one stop shop for all engineering branches, MBA, medicine, arts and science books'
        cat_info['meta_desc'] = meta_desc
        cat_info['meta_keywords'] = meta_desc
        sort_order+=1
        bs.write_to_cats_sheet(cat_info)
    sort_order = 0
    for subject in session.query(Subjects).all():
        cat_info['cat_id'] = subject.subject_id
        cat_info['parent_cat'] = subject.parent_branch_id
        cat_info['cat_name']  = subject.subject_name
        cat_info['q_isit_top'] = 'false'
        cat_info['sort_order'] = sort_order
        seo_list = subject.subject_name.split()
        seo_string = '_'.join(str(key_word) for key_word in seo_list)
        seo_string = seo_string+'_'+'Books'
        cat_info['seo_key_words'] = seo_string
        meta_desc = ' buy ' +subject.subject_name+ ' books online at collegekitab.com'
        meta_desc = meta_desc+ ' Collegekitab.com exclusively dedicated for academic books is favorite among students.'
        meta_desc = meta_desc+ ' at collegekitab.com you can not only buy books online, you can also buy used books or rent books on short term'
        meta_desc = meta_desc+ ' collegekitab.com is one stop shop for all engineering branches, MBA, medicine, arts and science books'
        cat_info['meta_desc'] = meta_desc
        cat_info['meta_keywords'] = meta_desc
        sort_order+=1
        bs.write_to_cats_sheet(cat_info)
    bs.save_wb() 
def convert_isbn13_to_string():
    for book_row in session.query(Books).all():
        book_row.book_isbn10 = str(book_row.book_isbn10)
        book_row.book_isbn13 = str(book_row.book_isbn13)
        print book_row.book_isbn13
        session.commit()
#now collect information and write onto the tables
populate_db()
#write_to_excel_file()
#convert_isbn13_to_string()

"""b_dict={}
for bk in session.query(Books).all():
    b_dict['product_id'] = bk.book_id
    b_dict['name'] = bk."""
"""for book_row in session.query(Books).all():
    print book_row, book_row.parent_subjects, book_row.book_id, book_row.related_books
for subject_row in session.query(Subjects).all():
    print subject_row, subject_row.subject_books
for branch_row in session.query(Branches).all():
    print branch_row
for main_cat in session.query(MainMenu).all():
    print main_cat, main_cat.menu_id"""
