delete from stock_move

select * from sale_order_line
delete from sale_order where id = 36
select * from mrp_bom 
delete from mrp_bom
delete from sale_order_line where sale_id = 36
select * from sale_order order by name
select * from product_template order by 3
delete from product_template where id = 2
select * from product_product
delete from product_template
delete from product_product where id in (3,4,5,6,7,8,9,10)
delete from product_product where id = 2
select * from product_category --116-117-118-119

update product_template set categ_id = 2
update product_template set categ_id = 116 where id in(18,19)

update product_template set categ_id = 116 where id in(18,19)
select id, name_template, product_tmpl_id from product_product order by 1
select id, name from product_template order by 1
update product_product set product_tmpl_id =27 where id =3
update product_product set product_tmpl_id =30 where id =4
update product_product set product_tmpl_id =29 where id =5
update product_product set product_tmpl_id =32 where id =7
update product_product set product_tmpl_id =33 where id =8
update product_product set product_tmpl_id =34 where id =9

select * from cyg_extras
select * from cyg_inmuebles_extras 
select * FROM procurement_order
DELETE FROM procurement_order WHERE ID =3



select * from res_partner_bank;
select * from res_bank ;