#coding=utf-8
import MySQLdb
import time

db = MySQLdb.connect("localhost", "root", "", "irtest", charset='utf8')
cursor = db.cursor()

page_map={}
page_demap={}
pr={}

def init():
    print 'start'

    sql="select count(*) from page"
    cursor.execute(sql)
    results = cursor.fetchall()
    total_page=results[0][0]

    page=0
    num_per_page=1000
    while 1:
        sql="select id,next,pr from page limit %d,%d" % (page*num_per_page,num_per_page)
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results)==0:
            break
        if page>9:
            break

        for row in results:
            page_map[row[0]]=row[1]
            pr[row[0]]=row[2]
        print 'loading:',(page+1)*num_per_page,'/',total_page
        page+=1

    print 'demapping...'
    count=0
    for page_id in page_map:
        print 'demap:',count,'/',total_page
        time.sleep(0.001)
        if page_map[page_id]==None or len(page_map[page_id])==0:
            page_map[page_id]=list(page_map)
        for next_id in page_map[page_id]:
            if not next_id in page_demap:
                page_demap[next_id]=[page_id]
            else:
                page_demap[next_id].append(page_id)
        count+=1

def pagerank(times):
    print 'start page rank'

    a=0.9
    max_iter=times
    min_delta=0.01
    map_size=len(page_map)
    beta=(1-a)/map_size
        
    delta_max=0

    for i in range(max_iter):
        print 'rank:',i
        for page_id in page_map:
            pr_old=pr[page_id]
            alpha=0
            for page_deid in page_demap[page_id]:
                alpha+=pr[page_deid]/len(page_map[page_deid])
            pr[page_id]=a*alpha+beta
            pr_delta=abs(pr[page_id]-pr_old)
            delta_max=max(delta_max,pr_delta)
        if delta_max<min_delta:
            break

def save():
    print 'saving...'
    total=len(page_map)
    count=0
    for key in pr:
        sql="update page set pr=%f where id=%d"%(pr[key],int(key))
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
        count+=1
        print 'saved:',count,'/',total
    print 'done.'

init()
pagerank(5)
save()
