#coding=utf-8

import requests
import bs4
import MySQLdb
import jieba
import re

root_url='http://www.view.sdu.edu.cn/'

invalid_url_word=['javascript','None','@','https://','www.','download','.jpg','.pdf','.jpeg','.doc']

db = MySQLdb.connect("localhost", "root", "", "irtest", charset='utf8')
cursor = db.cursor()

url_id={}

def dealpage(id,url):
    print url,
    res=requests.get(url)
    res.encoding='utf-8'
    soup=bs4.BeautifulSoup(res.text,'html.parser')
    
    #get text
    title=soup.select('title')
    if len(title)==0:
        title='无标题'
    else:
        title=soup.select('title')[0].text

    for s in soup('script'):
        s.extract() 
    for s in soup('style'):
        s.extract() 
    
    text=soup.text
    seg_list = jieba.cut_for_search(text)
    seg_list=list(set(seg_list))
    try:
        seg_list.remove('\'')
    except:
        pass
    seg_str= ' '.join(seg_list)
    
    #get next url

    next_url_list=[]

    url_now=url[0:url.rfind('/')]
    res.encoding='utf-8'
    for a_tag in soup.select('a'):
        next_url=str(a_tag.get('href'))
        #check 
        isclear=1
        for inv in invalid_url_word:
            if not next_url.find(inv)==-1:
                isclear=0
                break
        if isclear:
            if next_url.startswith('http://'):
                if not next_url.startswith(root_url):
                    continue
            elif next_url.startswith('/'):
                next_url=root_url+next_url[1:]
            elif next_url.startswith('../'):
                url_to=url_now
                while next_url.startswith('../'):
                    url_to=url_to[0:url_to.rfind('/')]
                    next_url=next_url[3:]
                next_url=url_to+'/'+next_url
            else:
                next_url=url_now+'/'+next_url
            next_url_list.append(geturlid(next_url))

    try:
        next_url_list=list(set(next_url_list))
        next_url_list.remove(-1)
    except:
        pass
    print next_url_list
    # update page
    
    next_url_str=' '.join(map(lambda x:str(int(x)),next_url_list))
    if not -1 in next_url_list:
        sql="update page set text='%s',title='%s',next='%s' where id=%d" % (seg_str,title,next_url_str,id)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

def geturlid(url):
    if url in url_id:
        return url_id[url]
    else:
        sql="select id from page where url='%s'"%(url)
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results)==0:
            return -1
        else:
            the_id=results[0][0]
            url_id[url]=the_id
            return the_id

def dealblankpage(num):
    sql="select id,url from page where text is null order by id desc limit 0,%d" % num
    cursor.execute(sql)
    results = cursor.fetchall()
    if len(results)==0:
        return 0
    for row in results:
        page_id= row[0]
        page_url= row[1]
        try:
            dealpage(page_id,page_url)
        except:
            pass
    return 1

while dealblankpage(500):
    pass