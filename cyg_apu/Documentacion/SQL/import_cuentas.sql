select * from cyg_jornada 
select * from product_uom 

﻿
--drop table import_cuentas;
	 
CREATE TABLE import_cuentas
(
  code character varying(200),
  name character varying(200),
  naturaleza character varying(200),
  mayor character varying(200)
  )
WITH (
  OIDS=FALSE
);
ALTER TABLE import_cuentas
  OWNER TO openerp;
  
--DELETE FROM import_cuentas where nro is null
DELETE FROM import_cuentas where code ='CUENTA'
COPY import_cuentas FROM '/tmp/import_pu.csv' DELIMITERS ',' CSV;
--COPY import_cuentas FROM '/home/edison/workspace/cyg/cyg_apu/Documentacion/import_pu.csv' DELIMITERS ',' CSV;

select * from import_cuentas order by 1
update import_cuentas set name = ltrim(name)
update import_cuentas set name = rtrim(name) --"QUE SE CARGA AL GASTO"
update import_cuentas set code = ltrim(code)
update import_cuentas set code = rtrim(code) --"QUE SE CARGA AL GASTO"


select * from import_cuentas where length(code) = 1 order by code
select * from import_cuentas where length(code) = 2 order by code
select * from import_cuentas where length(code) = 3 order by code
select * from import_cuentas where length(code) = 4 order by code
select * from import_cuentas where length(code) = 5 order by code
select * from import_cuentas where length(code) = 6 order by code

select * from import_cuentas where length(code) = 7 order by code
select * from import_cuentas where length(code) = 8 order by code

select * from import_cuentas where length(code) = 9 order by code
select * from import_cuentas where length(code) = 10 order by code

select max(length(code)) from import_cuentas where length(code) = 10 order by code
select * from import_cuentas where length(code) = 11 order by code
select * from import_cuentas where length(code) = 12 order by code

SELECT * FROM ir_actions_todo
UPDATE ir_actions_todo SET state = 'open' where id = 3
select * from wizard_multi_charts_accounts 
select * from ir_actions where id in (465,
498,
163,
398,
206
)
--"Set Your Accounting Options"
select * from res_company
update res_company set expects_chart_of_accounts= False
select * from res_users
SELECT company_id FROM account_account WHERE active = 't' AND account_account.parent_id IS NULL
SELECT * FROM account_account WHERE active = 't' AND account_account.parent_id IS NULL

select * from res_company

select * from account_move_line

select * from account_account
delete from account_account
delete from account_invoice 

select * from account_tax_template



SELECT cont_cuenta.codigo_cue,cont_registro.codigo_tipd,cont_registro.numdoc_reg,cont_registro.detalle_reg, (debe_reg-haber_reg)as monto, cont_diario.fecha_dia, cont_registro.codigo_cco, cont_diario.codigo_dia, (cont_registro.numdoc_reg)as no_comp, cont_registro.serial_reg 
FROM ((cont_diario RIGHT JOIN cont_registro 
ON cont_diario.serial_dia = cont_registro.serial_dia) LEFT JOIN cont_cuenta 
ON cont_registro.serial_cue = cont_cuenta.serial_cue) 
WHERE (((cont_diario.fecha_dia)>'2011-12-31' 
AND (cont_diario.fecha_dia)<'2014-11-20') 
AND ((cont_diario.serial_per)=15) 
AND ((cont_registro.fecha_trans) is NULL) 
AND (debe_reg-haber_reg)<>0 
/*AND (MONTH (cont_diario.fecha_dia) in(1,2,3,4))*/ 
AND CODIGO_TIPD IN ('II','IA','IP','IK','DI','DS',/*'FA',*/'DD','TS','CA','CD','NV', 'CC','NC') 
/*AND numdoc_reg in ('D-0281','D-0282')*/ /*AND codigo_cco like '%-%'*/)