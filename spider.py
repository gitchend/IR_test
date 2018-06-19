import requests
import bs4
import md5
import MySQLdb
import time

root_url='http://www.view.sdu.edu.cn/'

viewed_page=set()
page_queue=[]
invalid_url_word=['javascript','None','@','https://','www.','download','.jpg','.pdf','.jpeg','.doc']

db = MySQLdb.connect("localhost", "root", "", "irtest", charset='utf8')
cursor = db.cursor()

count=[0]

def printt(info):
    print unicode(info).encode('gbk','ignore')

def getPage(url):
    print url,count[0],len(page_queue)
    res=None
    try_time=0
    while 1:
        try:
            res=requests.get(url,timeout=5)
            break
        except:
            if try_time==2:
                break
            else:
                try_time+=1
    if res==None:
        return

    saveUrl(url)
    count[0]+=1

    url_now=url[0:url.rfind('/')]
    res.encoding='utf-8'
    soup=bs4.BeautifulSoup(res.text,'html.parser')
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

            if not next_url in viewed_page:
                print '--',next_url
                viewed_page.add(next_url)
                page_queue.append(next_url)

def saveUrl(url):
    sql="insert into page(url) values('%s')" % (url)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

def start():
    page_queue.append(root_url)

    while 1:
        if len(page_queue)==0:
            break
        url=page_queue[0]
        page_queue.pop(0)
        try:
            getPage(url)
        except:
            continue
        time.sleep(0.1)
    db.close()

if __name__=='__main__':
    start()
