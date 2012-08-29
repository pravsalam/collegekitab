cat_file ='sqls/cats.sql'
cat_desc_file = 'sqls/cats_desc.sql'
prod_file = 'sqls/prods.sql'
prod_attrs_file = 'sqls/prod_attrs.sql'
prod_desc_file = 'sqls/prod_descs.sql'
prod_opts_file = 'sqls/prod_options.sql'
prod_imgs_file = 'sqls/prod_images.sql'
prod_related_file = 'sqls/prod_relateds.sql'
prod_specials_file= 'sqls/prod_specials.sql'
prod_rewards_file = 'sqls/prod_rewards.sql'
cat_f = open(cat_file,'w')
cat_desc_f = open(cat_desc_file,'w')
prod_f = open(prod_file,'w')
prod_desc_f = open(prod_file,'w')
prod_attrs_f = open(prod_attrs_file,'w')
prod_desc_f = open(prod_desc_file,'w')
prod_options_f = open(prod_opts_file,'w')
prod_imgs_f = open(prod_imgs_file,'w')
prod_related_f = open(prod_related_file,'w')
prod_specials_f = open(prod_specials_file,'w')
prod_rewards_file  = open(prod_rewards_file,'w')

is_prods_first_time =True
is_prod_desc_first_time = True
is_prod_attrs_first_time = True
is_prod_options_first_time = True

def write_prods_sql(b_info):
    global is_prods_first_time
    if is_prods_first_time:
        prod_f.write('TRUNCATE TABLE `product`;\n\n\n')
        is_prods_first_time = False
    single_line = 'INSERT INTO `product` (`product_id`, `model`, `sku`, `upc`, `ean`, `jan`, `isbn`, `mpn`, `location`, `quantity`, `stock_status_id`, `image`, `manufacturer_id`, `shipping`, `price`, `points`, `tax_class_id`, `date_available`, `weight`, `weight_class_id`, `length`, `width`, `height`, `length_class_id`, `subtract`, `minimum`, `sort_order`, `status`, `date_added`, `date_modified`, `viewed`) VALUES ( '
    single_line = single_line+"'"+str(b_info['prod_id'])+"'"+','
    single_line = single_line+"'"+str(b_info['model'])+"'"+','
    single_line = single_line+"'', '', '', '', "
    single_line = single_line+"'"+str(b_info['isbn13'])+"'"+','
    single_line = single_line+"'', '', '100', '5',"
    single_line = single_line+"'"+"'"+b_info['image']+"'"+"'"+','
    single_line = single_line+"'0', '1',"
    single_line = single_line+"'"+str(float(b_info['price']))+"'"+','
    single_line = single_line+str(b_info['points'])+','
    single_line = single_line+"'0', '2012-08-24', '0.00000000', '1', '0.00000000', '0.00000000', '0.00000000', '1', '1', '1', '1', '1', '2012-08-25 19:13:18', '2012-08-25 19:17:24', '0');"
    print single_line 
    prod_f.write(single_line+'\n')
def write_prod_desc_sql(b_info):
    global is_prod_desc_first_time
    if is_prod_desc_first_time:
        prod_desc_f.write('TRUNCATE TABLE `product_description`;\n\n\n')
        is_prod_desc_first_time = False    
    single_line ='INSERT INTO `product_description` (`product_id`, `language_id`, `name`, `description`, `meta_description`, `meta_keyword`, `tag`) VALUES ('
    single_line = single_line+"'"+str(b_info['prod_id'])+"'"+","
    single_line = single_line+"'1'"+","
    single_line = single_line+"'"+b_info['name']+"'"+","
    if b_info['description']:
        single_line = single_line+"'"+b_info['description']+"'"+","
    else:
        single_line = single_line+"''"+","
    if b_info['meta_desc']:
        single_line = single_line+"'"+b_info['meta_desc']+"'"+","
    else:
        single_line = single_line+"''"+","
    if b_info['meta_keywords']:
        single_line = single_line+"'"+b_info['meta_keywords']+"'"+","+"'');"
    else:
        single_line = single_line+"''"+","+"'');"
    print single_line
    prod_desc_f.write(single_line+'\n') 
def write_prod_attrs_sql(b_info):
    global is_prod_attrs_first_time
    if is_prod_attrs_first_time:
        prod_attrs_f.write('TRUNCATE TABLE `product_attribute`;\n\n\n')
        is_prod_attrs_first_time= False 
    common_line = 'INSERT INTO `product_attribute` (`product_id`, `attribute_id`, `language_id`, `text`) VALUES ('
    prodid_line = common_line +"'"+str(b_info['prod_id'])+"'"+","
    
    #for authors
    authors_line = prodid_line +"'13'"+","+"'1'"+","+"'"+b_info['authors']+"'"+");"
    prod_attrs_f.write(authors_line+'\n')
    
    #for publisher
    publisher_line = prodid_line+"'14'"+","+"'1'"+","+"'"+b_info['publisher']+"'"+");"
    prod_attrs_f.write(publisher_line+'\n')
    
    #for isbn10 
    isbn10_line = prodid_line+"'15'"+","+"'1'"+","+"'"+b_info['isbn10']+"'"+");"
    prod_attrs_f.write(isbn10_line+'\n') 
    
    #for isbn13
    isbn13_line = prodid_line+"'16'"+","+"'1'"+","+"'"+b_info['isbn13']+"'"+");"
    prod_attrs_f.write(isbn13_line+'\n')
    
    #for publishing date
    if b_info['year_edition']:
        pub_date_line = prodid_line+"'17'"+","+"'1'"+","+"'"+b_info['year_edition']+"'"+");"
        prod_attrs_f.write(pub_date_line+'\n')
    #for edition 
    if b_info['edition']:
        edition_line = prodid_line+"'18'"+","+"'1'"+","+"'"+b_info['edition']+"'"+");"
        prod_attrs_f.write(edition_line+'\n')
    if b_info['pages']:
        pages_line = prodid_line+"'19'"+","+"'1'"+","+"'"+str(b_info['pages'])+"'"+");"
        prod_attrs_f.write(pages_line+'\n')
    #for bidning
    binding_line = prodid_line+"'20'"+","+"'1'"+","+"'Paperback'"+");"
    prod_attrs_f.write(binding_line+'\n')
    #for deliver
    delivery_line = prodid_line+"'21'"+","+"'1'"+","+"'1-4 Days delivery'"+");"
    prod_attrs_f.write(delivery_line+'\n')
def write_to_options_sql(b_info):
    global is_prod_options_first_time 
    if is_prod_options_first_time:
        prod_options_f.write('TRUNCATE TABLE `product_option_value`;\n\n\n')
        is_prod_options_first_time = False

    
    
    
    