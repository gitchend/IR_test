import MySQLdb

db = MySQLdb.connect("localhost", "root", "", "irtest", charset='utf8')
cursor = db.cursor()

id_page_now=[15,200]
word_map={}

def deal_pages_of_page():
    sql="select id,text from page limit %d,%d" % (id_page_now[0]*id_page_now[1],id_page_now[1])
    cursor.execute(sql)
    results = cursor.fetchall()
    if len(results)==0:
        return 0
    for row in results:
        page_id=row[0]
        page_text=row[1]
        if page_text==None:
            return 0
        dealpage(page_id,page_text)
    return 1

def dealpage(page_id,page_text):
    word_list=page_text.split(' ')
    for word in word_list:
        if not word in word_map:
            word_map[word]=[]
        word_map[word].append(page_id)

def saveword():
    for word in word_map:
        id_list=word_map[word]
        sql="select id,page_id from word where word='%s'"% word
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results)==0:
            id_list_str=' '.join(map(lambda x:str(int(x)),id_list))
            sql2="insert into word(word,page_id) values('%s','%s')"%(word,id_list_str)
            try:
                cursor.execute(sql2)
                db.commit()
            except:
                db.rollback()
        else:
            word_id=results[0][0]
            page_id_str=results[0][1]
            page_id_list=page_id_str.split(' ')
            id_list.extend(page_id_list)
            id_list=list(set(id_list))

            id_list_str=' '.join(map(lambda x:str(int(x)),id_list))
            sql2="update word set page_id='%s' where id=%d"%(id_list_str,word_id)
            try:
                cursor.execute(sql2)
                db.commit()
            except:
                db.rollback()
while 1:
    word_map={}
    print 'page:',id_page_now
    if not deal_pages_of_page():
        break
    id_page_now[0]+=1
    saveword()