from bs4 import BeautifulSoup
import urllib2
import re
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
isbn='9788131729717'
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
book_table = info_table.find('table')
if not book_table:
    book_table = info_table.find_next('div',attrs={'class':'contentbox_extreme_inner'}).find('table')
#iterate over table of book details 
# All the details are not available for every book
print("hello")
for tr in book_table.find_all('tr'):
    for td in tr.find_all('td'):
        left_string = td.get_text()
        key = left_string[:-1]
        print(key)
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
if 'name' in book_detailed_info_dict:
    book_info['name']=book_detailed_info_dict.get('name')+' by '+unicode(book_detailed_info_dict.get('authors'))
    book_info['seo_key_word']=seo_key_word
if 'authors' in  book_detailed_info_dict:
    book_info['authors'] = unicode(book_detailed_info_dict.get('authors'))
if 'isbn' in book_detailed_info_dict:
    book_info['isbn'] = book_detailed_info_dict.get('isbn')
if 'isbn_13' in book_detailed_info_dict:
    book_info['isbn_13']=book_detailed_info_dict.get('isbn_13')
if 'book_year' in book_detailed_info_dict:
    book_info['year_edition'] = book_detailed_info_dict.get('book_year')
if 'book_edition' in book_detailed_info_dict:
    book_info['edition'] = book_detailed_info_dict.get('book_edition')
if 'page_count' in book_detailed_info_dict:
    book_info['pages'] = int(book_detailed_info_dict.get('page_count'))
if 'book_publisher'in book_detailed_info_dict:
    book_info['publisher'] = book_detailed_info_dict.get('book_publisher')
book_info['image_name']='data/isbn/image_'+isbn
price_tag = ba_soup.find('div',attrs={'class':'pricingbox_inner'})
price_dict={'Price':'real_price',
            'Our Price':'discounted_price'}
price_value =0
for price_div_tag in price_tag.find_all('div'):
    for text_tag in price_div_tag('span'):
        key = text_tag.get_text().strip(':')
        if  price_dict.get(key)=='real_price':
            value_tag=text_tag.find_next('span')
            price_dict['Price'] =  int(value_tag.get_text()[3:])
        elif price_dict.get(key)=='discounted_price':
            print("did i enter here")
            value_tag = text_tag.find_next('span')
            discount_price = value_tag.get_text().replace(' ','')
            discount_price = discount_price.replace('Rs.','').strip()
            print(discount_price)
            price_dict['Our Price'] = int(discount_price)
book_info['price']=price_dict['Price']
book_info['points']=4*price_dict['Price']
our_price  = price_dict['Our Price']
priced_reduced_on_second_hand = price_reduced_on_used(our_price)
price_reduced_on_second_hand = price_reduced_on_used(our_price)
points_reduced_on_second_hand = price_reduced_on_second_hand/10
book_info['price_reduced_on_used'] = price_reduced_on_second_hand
book_info['points_reduced_on_used'] = points_reduced_on_second_hand
points_earned = our_price/10;
points_required = our_price*4
book_info['special_price']= our_price
book_info['points'] = points_required
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