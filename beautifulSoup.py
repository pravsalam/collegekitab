from bs4 import BeautifulSoup
from bs4 import NavigableString
import re
import urllib2
import xlwt
import bottlenose
import logging
import shutil
import xlrd
import datetime as dt
from xlutils.copy import copy
#global variables
product_id = 1 #it keeps increasing for everyproduct
wbk = xlwt.Workbook(encoding='UTF-8')
product_row = 0
options_row = 0
attrs_row = 0
specials_row = 0
rewards_row= 0 
cat_row = 0
logging.basicConfig(file='image_err.log',level=logging.DEBUG)
ws_cats = wbk.add_sheet('Categories')
ws_prods = wbk.add_sheet('Products')
ws_add_images = wbk.add_sheet('AdditionalImages')
ws_options = wbk.add_sheet('Options')
ws_attrs = wbk.add_sheet('Attributes')
ws_specials = wbk.add_sheet('Specials')

ws_rewards = wbk.add_sheet('Rewards')
#define headers for columns
# for categories 
"""ws_cats.write(cat_row,0,'category_id')
ws_cats.write(cat_row,1,'parent_id')
ws_cats.write(cat_row,2,'name')
ws_cats.write(0,3,'top')
ws_cats.write(0,4,'columns')
ws_cats.write(0,5,'sort_prder')
ws_cats.write(0,6,'image_name')
ws_cats.write(0,7,'date_added')
ws_cats.write(0,8,'date_modified')
ws_cats.write(0,9,'language_id')
ws_cats.write(0,10,'seo_keyword')
ws_cats.write(0,11,'description')
ws_cats.write(0,12,'meta_description')
ws_cats.write(0,13,'meta_keywords')
ws_cats.wrote(0,14,'store_ids')"""

#book_info = {} # dictionary to contain book details
#book_info['prod_id']
#book_info['name']
#book_info['image']
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
#end of globals
def price_reduced_on_used(our_price):
    if our_price<=150:
        price_reduced_on_second_hand = 30
    elif 150<our_price<=250:
        price_reduced_on_second_hand = 50
    elif 250<our_price<=350:
        price_reduced_on_second_hand = 80
    elif 350<our_price<=450:
        price_reduced_on_second_hand = 120
    elif 450<our_price<=750:
        price_reduced_on_second_hand = 150
    elif 750<our_price<=1000:
        price_reduced_on_second_hand = 200
    elif our_price>1000: 
        price_reduced_on_second_hand = 300
    return price_reduced_on_second_hand

def populate_book_info_fp(isbn):
    #product_id constant
    #print(isbn)
    url = 'http://www.flipkart.com/search/a/all?query='+isbn
    try:
        website= urllib2.urlopen(url, None, 90)
    except:
        return None
    web_html = website.read()
    soup = BeautifulSoup(web_html)
    if soup.find('div',attrs={'class':'no_results'}):
        return None
    # dectionary to be returned
    
    global product_id
    book_info ={}
    book_info['prod_id']=product_id
    #get book title
    class_tag = soup.find(attrs={'class':'mprod-summary'})
    if class_tag == None:
        return None
    name_title = class_tag.find(attrs={'itemprop':'name'})
    if name_title == None:
        return None
    book_name = name_title.string.strip()
    print(book_name)
    book_info['seo_key_word']=book_name.replace(" ","_")
    #get authors names
    authors_list = [authors.string for authors in soup.find_all('a',attrs={'href':re.compile("/author/.*?")})]
    try:
        authors_names = " ".join(authors_list)
    except:
        return None
    book_info['name'] = book_name #+ " by "+authors_names
    #book_info['authors'] = authors_names
    #get price
    #sometimes real price is the reduced price of item
    real_price =0
    our_price = 0
    price_tag = class_tag.find(id="fk-mprod-list-id")   
    our_price_tag = class_tag.find(id="fk-mprod-our-id")
    if price_tag != None and our_price_tag !=None:
        for original_price in price_tag.string.split():
            if original_price.isalnum():
                real_price = int(original_price)
        for content_our_price in our_price_tag.children:
            if isinstance(content_our_price,NavigableString):
                if content_our_price.isalnum():
                    our_price = int(content_our_price) - 30
    elif price_tag==None and our_price_tag!=None:
        for content_our_price in our_price_tag.children:
            if isinstance(content_our_price,NavigableString):
                if content_our_price.isalnum():
                    our_price = int(content_our_price) - 30
                    real_price = int(content_our_price)
    elif price_tag!=None and our_price_tag==None:
        for original_price in price_tag.string.split():
            if original_price.isalnum():
                try:
                    real_price = int(original_price)
                except:
                    return None
                our_price = real_price-30
    book_info['price'] = real_price
    book_info['special_price'] = our_price
    price_reduced_on_second_hand = price_reduced_on_used(our_price)
    points_reduced_on_second_hand = price_reduced_on_second_hand/10
    book_info['price_reduced_on_used'] = price_reduced_on_second_hand
    book_info['points_reduced_on_used'] = points_reduced_on_second_hand
    try:
        points_earned = our_price/10
    except:
        return None
    points_required = our_price*4
    book_info['special_price']= our_price
    book_info['points'] = points_required
    book_info['points_earned']=points_earned
    image_loc = 'data/isbn/'+'image_'+isbn
    book_info['image']=image_loc
    #get extra info like isbn,pages,edition
    book_extra_info_dict ={'Book':'book_name',
							'Author':'book_author',
							'ISBN':'book_isbn',
							'ISBN-13':'book_isbn_13',
							'Binding':'book_bind',
							'Publishing Date':'book_year',
							'Publisher':'book_publisher',
							'Edition':'book_edition',
							'Number of Pages':'book_page_count',
							'Language':'book_language'}
    book_detailed_info_dict={} #keys{name,authors,isbn,isbn_13,book_binding,book_year,book_publisher
    #book_edition,page_count,book_language
    #book_details = soup.find('div',attrs={'class':'item_left_column'})
    #book_table  = book_details.find('table')
    book_table = soup.find('table',attrs={'class':'fk-specs-type1'})
    #iterate over table of book details 
    # All the details are not available for every book
    if not book_table:
        return None
    for tr in book_table.find_all('tr'):
        for td in tr.find_all('td'):
            left_string = td.get_text()[:-1]
            key = left_string[:-1]
            if key in book_extra_info_dict:
                value = td.find_next('td').get_text()
                if book_extra_info_dict.get(key ) == 'book_name':
                    book_detailed_info_dict['name'] = value
                elif book_extra_info_dict.get(key ) =='book_author':
                    book_detailed_info_dict['authors']=value
                elif book_extra_info_dict.get(key) == 'book_isbn':
                    book_detailed_info_dict['isbn'] = value
                elif book_extra_info_dict.get(key) == 'book_isbn_13':
                    book_detailed_info_dict['isbn_13']=value
                elif book_extra_info_dict.get(key) == 'book_bind':
                    book_detailed_info_dict['book_binding'] = value
                elif book_extra_info_dict.get(key) == 'book_year':
                    book_detailed_info_dict['book_year']=value
                elif book_extra_info_dict.get(key) == 'book_publisher':
                    book_detailed_info_dict['book_publisher'] = value
                elif book_extra_info_dict.get(key) == 'book_edition':
                    book_detailed_info_dict['book_edition']= value;
                elif book_extra_info_dict.get(key) == 'book_page_count':
                    book_detailed_info_dict['page_count'] = value
                elif book_extra_info_dict.get(key) == 'book_language':
                    book_detailed_info_dict['book_language'] = value
    #print(book_detailed_info_dict)
    #not all the details are available in a table and we have already gathered some information with price.
    if 'authors' in  book_detailed_info_dict:
        book_info['authors'] = book_detailed_info_dict.get('authors')
        book_info['name'] = book_info['name']+' by '+book_info['authors']
    if 'isbn' in book_detailed_info_dict:
        book_info['isbn10'] = book_detailed_info_dict.get('isbn')
    if 'isbn_13' in book_detailed_info_dict:
        isbn13 = book_detailed_info_dict.get('isbn_13').split(',')[0]
        book_info['isbn13']=isbn13
    if 'book_year' in book_detailed_info_dict:
        book_info['year_edition'] = book_detailed_info_dict.get('book_year')
    if 'book_edition' in book_detailed_info_dict:
        book_info['edition'] = book_detailed_info_dict.get('book_edition')
    if 'page_count' in book_detailed_info_dict:
        try:
            book_info['pages'] = int(book_detailed_info_dict.get('page_count'))
        except:
            return None
    if 'book_publisher'in book_detailed_info_dict:
        book_info['publisher'] = book_detailed_info_dict.get('book_publisher')
    book_desc=[]
    desc_tag = soup.find('div',attrs={'class':'item_detail_details_left'})
    if desc_tag :
        desc_line = desc_tag.find(id='description_text')
        if desc_line:
            meta_desc=desc_line.get_text()
            for desc in desc_line.contents:
                book_desc.append(str(desc))
            book_info['description'] = " ".join(book_desc)
            book_info['meta_desc']= meta_desc[:300].strip('\r\n\t')
            book_info['meta_keywords'] = meta_desc[0:300].strip('\r\n\t')
            
    return book_info


def populate_book_desc(soup):
    print "hello"
    
def write_to_prod_sheet(book_info):
    global product_row
    print 'row = %d' %product_row 
    global ws_prods
    # start writing data All this variables are surely available no need to check if the keyword exists
    ws_prods.write(product_row,0,book_info['prod_id'])
    ws_prods.write(product_row,1,book_info['name'])
    ws_prods.write(product_row,7,book_info['isbn13'])
    ws_prods.write(product_row,10,100)
    ws_prods.write(product_row,14,'yes')
    if 'model' in book_info:
        ws_prods.write(product_row,11,book_info['model'])
    ws_prods.write(product_row,13,book_info['image'])
    ws_prods.write(product_row,15,book_info['price'])
    ws_prods.write(product_row,16,book_info['points'])
    ws_prods.write(product_row,30,book_info['seo_key_word'])
    ws_prods.write(product_row,17,dt.datetime.now().strftime("%Y-%d-%d %H:%M:%S"))
    ws_prods.write(product_row,18,dt.datetime.now().strftime("%Y-%d-%d %H:%M:%S"))
    ws_prods.write(product_row,19,dt.datetime.now().strftime("%Y-%d-%d"))
    ws_prods.write(product_row,20,0.00)
    ws_prods.write(product_row,21,'kg')
    ws_prods.write(product_row,22,0)
    ws_prods.write(product_row,23,0)
    ws_prods.write(product_row,24,0)
    ws_prods.write(product_row,25,'cm')
    ws_prods.write(product_row,26,'true') 
    ws_prods.write(product_row,27,0)
    ws_prods.write(product_row,28,0)
    ws_prods.write(product_row,29,1)
    ws_prods.write(product_row,34,6)                                            
    ws_prods.write(product_row,35,0)
    ws_prods.write(product_row,39,1)
    ws_prods.write(product_row,40,'true')
    ws_prods.write(product_row,41,1)
    if 'description' in book_info:
        ws_prods.write(product_row,31,book_info['description'])
    if 'meta_desc' in book_info:
        ws_prods.write(product_row,32,book_info['meta_desc'])
    if 'meta_keywords' in book_info:
        ws_prods.write(product_row,33,book_info['meta_keywords'])
    if 'parent_cats' in book_info:
        ws_prods.write(product_row,2,book_info['parent_cats'])
    if 'related_books' in book_info:
        ws_prods.write(product_row,37,book_info['related_books'])
    product_row+=1
def write_to_options_sheet(book_info):
    #print("to be continued")
    global options_row
    global ws_options
    #book condition new
    ws_options.write(options_row,0,book_info['prod_id'])
    ws_options.write(options_row,1,1)
    ws_options.write(options_row,2,'Book Condition')
    ws_options.write(options_row,3,'radio')
    ws_options.write(options_row,4,'New')
    ws_options.write(options_row,5,'')
    ws_options.write(options_row,6,'true')
    ws_options.write(options_row,7,50)
    ws_options.write(options_row,8,'true')
    ws_options.write(options_row,9,0.00)
    ws_options.write(options_row,10,'+')
    ws_options.write(options_row,11,0)
    ws_options.write(options_row,12,'+')
    ws_options.write(options_row,13,0.00)
    ws_options.write(options_row,14,'+')
    ws_options.write(options_row,15,1)
    options_row+=1
    #book condition for old
    ws_options.write(options_row,0,book_info['prod_id'])
    ws_options.write(options_row,1,1)
    ws_options.write(options_row,2,'Book Condition')
    ws_options.write(options_row,3,'radio')
    ws_options.write(options_row,4,'used')
    ws_options.write(options_row,5,'')
    ws_options.write(options_row,6,'true')
    ws_options.write(options_row,7,50)
    ws_options.write(options_row,8,'true')
    ws_options.write(options_row,9,book_info['price_reduced_on_used'])
    ws_options.write(options_row,10,'-')
    ws_options.write(options_row,11,book_info['points_reduced_on_used'])
    ws_options.write(options_row,12,'-')
    ws_options.write(options_row,13,0.00)
    ws_options.write(options_row,14,'+')
    ws_options.write(options_row,15,2)
    options_row+=1
    #rent option for 1 week
    ws_options.write(options_row,0,book_info['prod_id'])
    ws_options.write(options_row,1,1)
    ws_options.write(options_row,2,'Rent The Book For')
    ws_options.write(options_row,3,'select')
    ws_options.write(options_row,4,'1 Week')
    ws_options.write(options_row,5,'no_image.jpg')
    ws_options.write(options_row,6,'false')
    ws_options.write(options_row,7,100)
    ws_options.write(options_row,8,'true')
    ws_options.write(options_row,9,0.00)
    ws_options.write(options_row,10,'+')
    ws_options.write(options_row,11,0)
    ws_options.write(options_row,12,'+')
    ws_options.write(options_row,13,0.00)
    ws_options.write(options_row,14,'+')
    ws_options.write(options_row,15,0)
    options_row+=1
    #rent option for 2 weeks
    ws_options.write(options_row,0,book_info['prod_id'])
    ws_options.write(options_row,1,1)
    ws_options.write(options_row,2,'Rent The Book For')
    ws_options.write(options_row,3,'select')
    ws_options.write(options_row,4,'2 Week')
    ws_options.write(options_row,5,'no_image.jpg')
    ws_options.write(options_row,6,'false')
    ws_options.write(options_row,7,100)
    ws_options.write(options_row,8,'true')
    ws_options.write(options_row,9,0.00)
    ws_options.write(options_row,10,'+')
    ws_options.write(options_row,11,0)
    ws_options.write(options_row,12,'+')
    ws_options.write(options_row,13,0.00)
    ws_options.write(options_row,14,'+')
    ws_options.write(options_row,15,1)
    options_row+=1
    #rent option for 3 weeks
    ws_options.write(options_row,0,book_info['prod_id'])
    ws_options.write(options_row,1,1)
    ws_options.write(options_row,2,'Rent The Book For')
    ws_options.write(options_row,3,'select')
    ws_options.write(options_row,4,'3 Week')
    ws_options.write(options_row,5,'no_image.jpg')
    ws_options.write(options_row,6,'false')
    ws_options.write(options_row,7,100)
    ws_options.write(options_row,8,'true')
    ws_options.write(options_row,9,0.00)
    ws_options.write(options_row,10,'+')
    ws_options.write(options_row,11,0)
    ws_options.write(options_row,12,'+')
    ws_options.write(options_row,13,0.00)
    ws_options.write(options_row,14,'+')
    ws_options.write(options_row,15,2)
    options_row+=1
    
    #rent option for 1 Month
    ws_options.write(options_row,0,book_info['prod_id'])
    ws_options.write(options_row,1,1)
    ws_options.write(options_row,2,'Rent The Book For')
    ws_options.write(options_row,3,'select')
    ws_options.write(options_row,4,'1 Month')
    ws_options.write(options_row,5,'no_image.jpg')
    ws_options.write(options_row,6,'false')
    ws_options.write(options_row,7,100)
    ws_options.write(options_row,8,'true')
    ws_options.write(options_row,9,0.00)
    ws_options.write(options_row,10,'+')
    ws_options.write(options_row,11,0)
    ws_options.write(options_row,12,'+')
    ws_options.write(options_row,13,0.00)
    ws_options.write(options_row,14,'+')
    ws_options.write(options_row,15,2)
    options_row+=1
def write_to_attrs_sheet(book_info):
    global ws_attrs
    global attrs_row
    #write author attribute
    ws_attrs.write(attrs_row,0,book_info['prod_id'])
    ws_attrs.write(attrs_row,1,1)
    ws_attrs.write(attrs_row,2,'Book details')
    ws_attrs.write(attrs_row,3,'Author')
    ws_attrs.write(attrs_row,4,book_info['authors'])
    attrs_row+=1
    
    #write publisher
    ws_attrs.write(attrs_row,0,book_info['prod_id'])
    ws_attrs.write(attrs_row,1,1)
    ws_attrs.write(attrs_row,2,'Book details')
    ws_attrs.write(attrs_row,3,'publisher')
    ws_attrs.write(attrs_row,4,book_info['publisher'])
    attrs_row+=1
    
    #write Edition row
    ws_attrs.write(attrs_row,0,book_info['prod_id'])
    ws_attrs.write(attrs_row,1,1)
    ws_attrs.write(attrs_row,2,'Book details')
    ws_attrs.write(attrs_row,3,'Edition')
    if 'edition' in book_info:
        ws_attrs.write(attrs_row,4,book_info['edition'])
    else:
        ws_attrs.write(attrs_row,4,'')
    attrs_row+=1
    
    #write isbn
    ws_attrs.write(attrs_row,0,book_info['prod_id'])
    ws_attrs.write(attrs_row,1,1)
    ws_attrs.write(attrs_row,2,'Book details')
    ws_attrs.write(attrs_row,3,'ISBN')
    if 'isbn10' in book_info:
        ws_attrs.write(attrs_row,4,book_info['isbn10'])
    else:
        ws_attrs.write(attrs_row,4,'')
    attrs_row+=1
    
    #write ISBN-13
    ws_attrs.write(attrs_row,0,book_info['prod_id'])
    ws_attrs.write(attrs_row,1,1)
    ws_attrs.write(attrs_row,2,'Book details')
    ws_attrs.write(attrs_row,3,'ISBN-13')
    if 'isbn13' in book_info:
        ws_attrs.write(attrs_row,4,book_info['isbn13'])
    else:
        ws_attrs.write(attrs_row,4,'')
    attrs_row+=1
    
    #write publishing date
    ws_attrs.write(attrs_row,0,book_info['prod_id'])
    ws_attrs.write(attrs_row,1,1)
    ws_attrs.write(attrs_row,2,'Book details')
    ws_attrs.write(attrs_row,3,'Publishing date')
    if 'year_edition' in book_info:
        ws_attrs.write(attrs_row,4,book_info['year_edition'])
    else:
        ws_attrs.write(attrs_row,4,'')
    attrs_row+=1
    
    #write page count
    ws_attrs.write(attrs_row,0,book_info['prod_id'])
    ws_attrs.write(attrs_row,1,1)
    ws_attrs.write(attrs_row,2,'Book details')
    ws_attrs.write(attrs_row,3,'Number of Pages')
    if 'pages' in book_info:
        ws_attrs.write(attrs_row,4,book_info['pages'])
    else:
        ws_attrs.write(attrs_row,4,'')
    attrs_row+=1
    #write delivery
    ws_attrs.write(attrs_row,0,book_info['prod_id'])
    ws_attrs.write(attrs_row,1,1)
    ws_attrs.write(attrs_row,2,'Delivery &amp; Payment')
    ws_attrs.write(attrs_row,3,'Delivery')
    ws_attrs.write(attrs_row,4,'1-4 days')
    attrs_row+=1
    
    #write Available for rent location
    ws_attrs.write(attrs_row,0,book_info['prod_id'])
    ws_attrs.write(attrs_row,1,1)
    ws_attrs.write(attrs_row,2,'Delivery &amp; Payment')
    ws_attrs.write(attrs_row,3,'Available in')
    ws_attrs.write(attrs_row,4,'Bangalore')
    attrs_row+=1
    
#def write our prices to the specials sheet
def write_to_specials_sheet(book_info):
    global specials_row
    global ws_specials
    ws_specials.write(specials_row,0,book_info['prod_id'])
    ws_specials.write(specials_row,1,'Default')
    ws_specials.write(specials_row,2,1)
    ws_specials.write(specials_row,4,'0000-00-00')
    ws_specials.write(specials_row,5,'0000-00-00')
    ws_specials.write(specials_row,3,book_info['special_price'])
    specials_row+=1
    
def write_to_rewards_sheet(book_info):
    global rewards_row
    global ws_rewards
    ws_rewards.write(rewards_row,0,book_info['prod_id'])
    ws_rewards.write(rewards_row,1,'Default')
    ws_rewards.write(rewards_row,2,book_info['points_earned'])
    rewards_row+=1
def write_to_cats_sheet(cat_info):
    global cat_row
    global ws_cats
    ws_cats.write(cat_row,0,cat_info['cat_id'])
    ws_cats.write(cat_row,1,cat_info['parent_cat'])
    ws_cats.write(cat_row,2,cat_info['cat_name'])
    ws_cats.write(cat_row,3,cat_info['q_isit_top'])
    ws_cats.write(cat_row,4,5)
    ws_cats.write(cat_row,5,cat_info['sort_order'])
    ws_cats.write(cat_row,7,dt.datetime.now().strftime("%Y-%d-%d %H:%M:%S"))
    ws_cats.write(cat_row,8,dt.datetime.now().strftime("%Y-%d-%d %H:%M:%S"))
    ws_cats.write(cat_row,9,1)
    ws_cats.write(cat_row,10,cat_info['seo_key_words'])
    ws_cats.write(cat_row,12,cat_info['meta_desc'])
    ws_cats.write(cat_row,13,cat_info['meta_keywords'])
    ws_cats.write(cat_row,14,0)
    ws_cats.write(cat_row,16,'true')
    cat_row+=1
def save_wb():
    wbk.save('products.xls')

def download_prod_img_from_fk(isbn):
    print("fetching pic from flipkart")
    url = 'http://www.flipkart.com/search/a/all?query='+isbn
    try:
        website= urllib2.urlopen(url, None, 90)
    except:
        return None
    web_html = website.read()
    soup = BeautifulSoup(web_html)
    if soup.find('div',attrs={'class':'no_results'}):
        return None
    image_parent_div_tag = soup.find('div', id='mprodimg-id')
    if image_parent_div_tag == None:
        image_parent_div_tag = soup.find('div',id='main-image-id')
    if image_parent_div_tag:
        try:
            image_url = dict(image_parent_div_tag.find('img').attrs).get('src')
        except:
            image_url = dict(soup.find('div',id='main-image-id').find('img').attrs).get('src')
        print(image_url)
        try:
            image_data = urllib2.urlopen(image_url,None,90).read()
        except:
            logging.info('unable to download image fp for isbn %s',isbn)
            return 0
        isbn=isbn.strip()
        img_file_name = 'isbn/image_'+isbn+'.jpg'
        print(img_file_name)
        image_write_file = open(img_file_name,'wb')
        image_write_file.write(image_data)
        image_write_file.close()
        
        return 1
    else:
        logging.info('image download from fp failed for %s',isbn)
        return 0
def download_prod_img_from_ba(isbn):
    print("fetching pic from bookadda")
    ba_url='http://www.bookadda.com/general-search?searchkey='+isbn
    print(ba_url)
    ba_web = urllib2.urlopen(ba_url)
    ba_soup=BeautifulSoup(ba_web.read())
    img_div_tag = ba_soup.find('div',attrs={'class':'main_img'})
    if img_div_tag:
        image_url = dict(img_div_tag.find('img').attrs).get('src')
        print(image_url)
        try:
            image_data = urllib2.urlopen(image_url,None,90).read()
        except:
            logging.info('unable to download image from bookadda for isbn %s',isbn)
            return 0
        isbn=isbn.strip()
        img_file_name = 'isbn/image_'+isbn+'.jpg'
        print(img_file_name)
        image_write_file = open(img_file_name,'wb')
        image_write_file.write(image_data)
        image_write_file.close()
        return 1
    else:
        logging.info('unable to download image from bookadda for isbn %s',isbn)
        return 0
     
def download_prod_img(isbn):
    #first try to download image from
    stripped_isbn=isbn.strip() 
    AWS_KEY = "AWS_KEY" # this won't work,get aws key
    SECRET_KEY = "AWSK_SECRET_KEY" #this won't work, get aws secret key
    ASSOCIATE_TAG = "wwwgetgreacom-20"
    api = bottlenose.Amazon(AWS_KEY,SECRET_KEY,ASSOCIATE_TAG,"ItemLookup")
    root = api.ItemLookup(ItemId=stripped_isbn,IdType="ISBN",SearchIndex="Books" ,  ResponseGroup="Large")
    amzn_soup = BeautifulSoup(root)
    fpk_rescue=0
    ba_rescue=0
    isbn=isbn.strip()
    if amzn_soup.find('error'):
        print('amazon failed')
        logging.info('image download from amazon failed for %s',isbn)
        fpk_rescue=1
    else:
        large_image_tag= amzn_soup.find('largeimage')
        if large_image_tag!=None:
            i=0
            for urls in large_image_tag.find_all('url'):
                try:
                    image_data = urllib2.urlopen(urls.get_text(),None,90).read()
                    if i==0:
                        img_file_name = 'isbn/image_'+isbn+'.jpg'
                        i+=1
                    else:
                        img_file_name='isbn/image_'+str(i)+'_'+isbn+'.jpg'
                        i+=1
                    print(img_file_name)
                    image_write_file = open(img_file_name,'wb')
                    image_write_file.write(image_data)
                    image_write_file.close()
                    print('pic from amazon')
                    return 1
                except:
                    fpk_rescue=1
                    break
        else:
            fpk_rescue=1
    if fpk_rescue==1:
        print('fetching from flipkart')
        if download_prod_img_from_fk(isbn):# try from flipkart
            print('flipkart image successful')
            return 1
        else:
            ba_rescue=1
        #now try from bookadda
    if ba_rescue==1:
            return download_prod_img_from_ba(isbn)

def populate_book_info_bookadda(isbn):
    book_info={}
    ba_url='http://www.bookadda.com/general-search?searchkey='+isbn
    ba_web = urllib2.urlopen(ba_url)
    ba_soup=BeautifulSoup(ba_web.read())
    book_extra_info_dict ={'Book':'book_name',
                            'Author':'book_author',
                            'ISBN':'book_isbn',
                            'ISBN-13':'book_isbn_13',
                            'Binding':'book_bind',
                            'Publishing Date':'book_year',
                            'Publisher':'book_publisher',
                            'Edition':'book_edition',
                            'Number of Pages':'book_page_count',
                            'Language':'book_language'}
    book_detailed_info_dict={} #keys{name,authors,isbn,isbn_13,book_binding,book_year,book_publisher
    #book_edition,page_count,book_language
    #book_details = soup.find('div',attrs={'class':'item_left_column'})
    #book_table  = book_details.find('table')
    info_table = ba_soup.find('div',attrs={'class':'contentbox_extreme_inner'})
    if not info_table:
        return None
    book_table = info_table.find('table')
    if not book_table:
        book_table = info_table.find_next('div',attrs={'class':'contentbox_extreme_inner'}).find('table')
    if not book_table:
        return None
    #iterate over table of book details 
    # All the details are not available for every book
    for tr in book_table.find_all('tr'):
        for td in tr.find_all('td'):
            left_string = td.get_text()
            key = left_string[:-1]
            if key in book_extra_info_dict:
                value = td.find_next('td').get_text()
                if book_extra_info_dict.get(key ) == 'book_name':
                    book_detailed_info_dict['name'] = value
                elif book_extra_info_dict.get(key ) =='book_author':
                    value.replace(u'\xa0',u'')
                    book_detailed_info_dict['authors']=value.replace('\t','').replace('\n','').replace(u'\xa0',u'').replace('\r','').strip()
                elif book_extra_info_dict.get(key) == 'book_isbn':
                    book_detailed_info_dict['isbn'] = value
                elif book_extra_info_dict.get(key) == 'book_isbn_13':
                    book_detailed_info_dict['isbn_13']=value
                elif book_extra_info_dict.get(key) == 'book_bind':
                    book_detailed_info_dict['book_binding'] = value
                elif book_extra_info_dict.get(key) == 'book_year':
                    book_detailed_info_dict['book_year']=value
                elif book_extra_info_dict.get(key) == 'book_publisher':
                    book_detailed_info_dict['book_publisher'] = value
                elif book_extra_info_dict.get(key) == 'book_edition':
                    book_detailed_info_dict['book_edition']= value;
                elif book_extra_info_dict.get(key) == 'book_page_count':
                    book_detailed_info_dict['page_count'] = value
                elif book_extra_info_dict.get(key) == 'book_language':
                    book_detailed_info_dict['book_language'] = value
    #print(book_detailed_info_dict)
    #not all the details are available in a table and we have already gathered some information with price.
    seo_key_word = book_detailed_info_dict.get('name').replace(' ','_')
    book_info['prod_id']=product_id
    isbn = isbn.strip()
    book_info['image'] = 'isbn/image_'+isbn
    if 'name' in book_detailed_info_dict:
        book_info['name']=book_detailed_info_dict.get('name')+' by '
        first_time = 1
        try:
            for authors in book_detailed_info_dict.get('authors').split(' '):
                if first_time:
                    book_info['name']= book_info['name']+' '+unicode(authors)
                else:
                    book_info['name'] = book_info['name']+','+unicode(authors)
        except:
            return None
        book_info['seo_key_word']=seo_key_word
    if 'authors' in  book_detailed_info_dict:
        book_info['authors'] = unicode(book_detailed_info_dict.get('authors'))
    if 'isbn' in book_detailed_info_dict:
        book_info['isbn10'] = book_detailed_info_dict.get('isbn')
    if 'isbn_13' in book_detailed_info_dict:
        book_info['isbn13']=book_detailed_info_dict.get('isbn_13')
    if 'book_year' in book_detailed_info_dict:
        book_info['year_edition'] = book_detailed_info_dict.get('book_year')
    if 'book_edition' in book_detailed_info_dict:
        book_info['edition'] = book_detailed_info_dict.get('book_edition')
    if 'page_count' in book_detailed_info_dict:
        pages_string = book_detailed_info_dict.get('page_count').replace(',','')
        book_info['pages'] = int(pages_string.split('.')[0])
    if 'book_publisher'in book_detailed_info_dict:
        book_info['publisher'] = book_detailed_info_dict.get('book_publisher')
    book_info['image']='data/isbn/image_'+isbn
    price_tag = ba_soup.find('div',attrs={'class':'prcbox'})
    price_dict={'Price':'real_price',
                'Our Price':'discounted_price'}
    # bookadda changed their style of pricing
    """for price_div_tag in price_tag.find_all('div'):
        for text_tag in price_div_tag('span'):
            key = text_tag.get_text().strip(':')
            if  price_dict.get(key)=='real_price':
                value_tag=text_tag.find_next('span')
                price_dict['Price'] =  int(value_tag.get_text()[3:])
            elif price_dict.get(key)=='discounted_price':
                value_tag = text_tag.find_next('span')
                discount_price = value_tag.get_text().replace(' ','')
                discount_price = discount_price.replace('Rs.','').strip()
                price_dict['Our Price'] = int(discount_price)"""
    price_table_tag = price_tag.find('table')
    for tr in price_table_tag.find_all('tr'):
        for td in tr.find_all('td'):
            key = td.get_text()
            if key == 'Price:':
                key = key[:-1]
            if price_dict.get(key) == 'real_price':
                value = td.find_next('td').find_next('td').get_text()[3:]
                price_dict['Price'] = int(value)
            elif price_dict.get(key)=='discounted_price':
                value = td.find_next('td').find_next('td').get_text()[3:]
                price_dict['Our Price'] = int(value)
            
    book_info['price']=price_dict['Price']
    book_info['points']=4*price_dict['Price']
    our_price  = price_dict['Our Price']
    price_reduced_on_second_hand = price_reduced_on_used(our_price)
    points_reduced_on_second_hand = price_reduced_on_second_hand/10
    book_info['price_reduced_on_used'] = price_reduced_on_second_hand
    book_info['points_reduced_on_used'] = points_reduced_on_second_hand
    try:
        points_earned = our_price/10
    except:
        return None
    points_required = our_price*4
    book_info['special_price']= our_price
    book_info['points'] = points_required
    book_info['points_earned']=points_earned
    #get the description
    book_desc=[]
    desc_line = ba_soup.find('div',attrs={'class':'reviews-box-cont-inner'})
    if desc_line != None:
        meta_desc=desc_line.get_text()
        for desc in desc_line.contents:
            book_desc.append(str(desc))
        book_info['description'] = " ".join(book_desc)
        book_info['meta_desc']= meta_desc[:300].strip('\r\n\t')
        book_info['meta_keywords'] = meta_desc[0:300].strip('\r\n\t')
    return book_info
def populate_book_info_uread(isbn):
    book_info={}
    ur_url='http://www.uread.com/search-books/'+isbn
    ur_web = urllib2.urlopen(ur_url)
    ur_soup=BeautifulSoup(ur_web.read())
    book_extra_info_dict ={'Book':'book_name',
                            'Author':'book_author',
                            'ISBN-10':'book_isbn',
                            'ISBN-13':'book_isbn_13',
                            'Binding':'book_bind',
                            'Publisher Date':'book_year',
                            'Publisher':'book_publisher',
                            'Edition':'book_edition',
                            'No of Pages':'book_page_count',
                            'Language':'book_language'}
    book_detailed_info_dict={} #keys{name,authors,isbn,isbn_13,book_binding,book_year,book_publisher
    #book_edition,page_count,book_language
    #book_details = soup.find('div',attrs={'class':'item_left_column'})
    #book_table  = book_details.find('table')
    info_div = ur_soup.find('div',id ='bookdetail')
    if not info_div:
        return None
    book_table = info_div.find('table')
    if not book_table:
        return None
    for tr in book_table.find_all('tr'):
        for td in tr.find_all('td'):
            total_string = td.get_text()
            key = total_string.split(':')[0]
            value = total_string.split(':')[1]
            if key in book_extra_info_dict:
                #value = td.find_next('td').get_text()
                if book_extra_info_dict.get(key ) == 'book_name':
                    book_detailed_info_dict['name'] = value
                elif book_extra_info_dict.get(key ) =='book_author':
                    value.replace(u'\xa0',u'')
                    book_detailed_info_dict['authors']=value.replace('\t','').replace('\n','').replace(u'\xa0',u'').replace('\r','').strip()
                elif book_extra_info_dict.get(key) == 'book_isbn':
                    book_detailed_info_dict['isbn'] = value
                elif book_extra_info_dict.get(key) == 'book_isbn_13':
                    book_detailed_info_dict['isbn_13']=value
                elif book_extra_info_dict.get(key) == 'book_bind':
                    book_detailed_info_dict['book_binding'] = value
                elif book_extra_info_dict.get(key) == 'book_year':
                    book_detailed_info_dict['book_year']=value
                elif book_extra_info_dict.get(key) == 'book_publisher':
                    book_detailed_info_dict['book_publisher'] = value
                elif book_extra_info_dict.get(key) == 'book_edition':
                    book_detailed_info_dict['book_edition']= value;
                elif book_extra_info_dict.get(key) == 'book_page_count':
                    book_detailed_info_dict['page_count'] = int(value)
                elif book_extra_info_dict.get(key) == 'book_language':
                    book_detailed_info_dict['book_language'] = value
    # copy info to book_info
    if 'isbn' in book_detailed_info_dict:
        book_info['isbn10'] = book_detailed_info_dict.get('isbn')
    if 'isbn_13' in book_detailed_info_dict:
        book_info['isbn13']=book_detailed_info_dict.get('isbn_13')
    if 'book_year' in book_detailed_info_dict:
        book_info['year_edition'] = book_detailed_info_dict.get('book_year')
    if 'book_edition' in book_detailed_info_dict:
        book_info['edition'] = book_detailed_info_dict.get('book_edition')
    if 'page_count' in book_detailed_info_dict:
        book_info['pages'] = int(book_detailed_info_dict.get('page_count'))
    if 'book_publisher'in book_detailed_info_dict:
        book_info['publisher'] = book_detailed_info_dict.get('book_publisher')
        
    title_tag = ur_soup.find('div',attrs={'class':'product-title'})
    name_tag = title_tag.find('label',id='ctl00_phBody_ProductDetail_lblTitle')
    book_name = name_tag.get_text()
    book_detailed_info_dict['name'] = book_name
    authors_tag = title_tag.find('p')
    author_list=[]
    for author_tag in authors_tag.find_all('a'):
        author_list.append(author_tag.get_text())
    authors_string = ','.join(author for author in author_list)
    print authors_string
    book_info['name'] = book_name +' by '+authors_string
    book_info['authors'] = authors_string
    prices_tag = ur_soup.find('div',attrs={'class':'product-prices'})
    #list price
    list_price_tag = prices_tag.find('p',attrs={'class':'list-price'})
    try:
        real_price = int(list_price_tag.get_text().split(':')[1].strip()[1:])
    except:
        return None
    book_info['price'] = real_price
    #discounted price
    disc_price_tag = prices_tag.find('p',attrs={'class':'our-price'})
    our_price = int(disc_price_tag.get_text().split(':')[1].strip()[1:])
    book_info['special_price']= our_price
    price_reduced_on_second_hand = price_reduced_on_used(our_price)
    points_reduced_on_second_hand = int(price_reduced_on_second_hand/10)
    book_info['price_reduced_on_used'] = price_reduced_on_second_hand
    book_info['points_reduced_on_used'] = points_reduced_on_second_hand
    seo_key_word = book_info.get('name').replace(' ','_')
    book_info['prod_id']=product_id
    isbn = isbn.strip()
    book_info['image'] = 'isbn/image_'+isbn
    book_info['seo_key_word'] = seo_key_word
    try:
        points_earned = our_price/10
    except:
        return None
    points_required = our_price*4
    book_info['points'] = points_required
    book_info['points_earned']=points_earned
    book_desc=[]
    desc_line = ur_soup.find('div',id='aboutbook')
    if desc_line != None:
        meta_desc=desc_line.get_text()
        for desc in desc_line.contents:
            book_desc.append(desc.get_text())
        book_info['description'] = " ".join(book_desc)
        book_info['meta_desc']= meta_desc[:300].strip('\r\n\t')
        book_info['meta_keywords'] = meta_desc[0:300].strip('\r\n\t')
    return book_info
#in a for loop get isbns9
"""isbn_list = open('file.txt',"r")
print("oh no")
for isbn in isbn_list:
    url=''
    if(isbn=='\n'):
        exit()
    # populate book_info dictionary
    book_info= populate_book_info_fp(isbn)  
    if not book_info:
        #get book info from bookadda
        book_info = populate_book_info_bookadda(isbn)
    book_info=populate_book_info_uread(isbn)
    isbn = isbn.strip()
    if not download_prod_img(isbn):
        logging.info('unable to download image for isbn %s',isbn)
        destin_img='isbn/noimage_cklogo_'+isbn+'.jpg'
        shutil.copy2('cklogo.jpg',destin_img)
    print(product_id)    
    #book_info['prod_id']='hi'
       
    print(book_info)
    #write data to workbooks 
    write_to_prod_sheet(book_info)
    write_to_options_sheet(book_info)
    write_to_attrs_sheet(book_info)
    write_to_specials_sheet(book_info)
    write_to_rewards_sheet(book_info)
    #for next loop increase rows
    product_row+=1
    options_row+=1
    attrs_row+=1
    specials_row+=1
    rewards_row+=1 
    product_id+=1
    wbk.save('products.xls')
wbk.save('products.xls')"""
