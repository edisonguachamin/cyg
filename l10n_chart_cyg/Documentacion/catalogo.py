import psycopg2
conn_string = "host='localhost' dbname='cyg' user='postgres' password='postgres'"
# print the connection string we will use to connect
print "Connecting to database\n	->%s" % (conn_string)

# get a connection, if a connect cannot be made an exception will be raised here
conn = psycopg2.connect(conn_string)

# conn.cursor will return a cursor object, you can use this cursor to perform queries
cr = conn.cursor()
#sql = "select * from import_cuentas where length(code) = 3 order by code" #101
sql = "select * from import_cuentas order by code"
cr.execute(sql)
res = cr.fetchall()

for item in res:
	code = item[0]
	id  = code
	#print 'code', code
	parent= ''
	if len(code) == 2:
		parent = code[0:1]
	elif len(code) == 3:
		parent = code[0:1]
	elif len(code) == 4:
		parent = code[0:2]
	elif len(code) == 5:
		parent = code[0:3]
	elif len(code) == 6:
		parent = code[0:4]
	elif len(code) == 7:
		parent = code[0:5]
	elif len(code) == 8:
		parent = code[0:6]
	elif len(code) == 9:
		parent = code[0:7]
	elif len(code) == 10:
		parent = code[0:8]
	elif len(code) == 11:
		parent = code[0:9]
	elif len(code) == 12:
		parent = code[0:9]
	elif len(code) == 1:
		parent = '0'
	type = ''
	if item[3]=='M':
		type ='view'
		type_view = 'account_type_view'
	else:
		type ='other'
		type_view = 'account_type_asset'
	data = "<record model='account.account.template' id='cyg_"+id+"'>"\
	"<field name='name'>"+item[1]+"</field><field name='code'>"+code+"</field>"\
	"<field name='reconcile' eval='False'/>"\
	"<field ref='"+type_view+"' name='user_type'/>"\
    "<field name='type'>"+type+"</field>"\
    "<field ref='cyg_"+parent+"' name='parent_id'/>"\
	"</record>"
	"""
	
	"""
	print data
