cat_file ='sqls/cats.sql'
cat_desc_file = 'sql/cats_desc.sql'
prod_file = 'sqls/prods.sql'
prod_attrs_file = 'sqls/prod_attrs.sql'
prod_desc_file = 'sqls/prod_descs.sql'
prod_opts_file = 'sql/prod_options.sql'
prod_imgs_file = 'sql/prod_images.sql'
prod_related_file = 'sql/prod_relateds.sql'
prod_specials_file= 'sql/prod_specials.sql'
prod_rewards_file = 'sql/prod_rewards.sql'
cat_f = open(cat_file)
cat_desc_f = open(cat_desc_file)
prod_f = open(prod_file)
prod_attrs_f = open(prod_attrs_file)
prod_desc_f = open(prod_desc_file)
prod_opts_f = open(prod_opts_file)
prod_imgs_f = open(prod_imgs_file)
prod_related_f = open(prod_related_file)
prod_specials_f = open(prod_specials_file)
prod_rewards_file  = open(prod_rewards_file)


def write_prods_sql()