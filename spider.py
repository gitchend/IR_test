import requests
import bs4
import md5
import MySQLdb

root_url='http://www.view.sdu.edu.cn/'

viewed_page=set()
page_queue=[]
invalid_url_word=['http','javascript','None','@']

def printt(info):
    print unicode(info).encode('gbk','ignore')

def getPage(url):
    print url
    res=requests.get(url)
    res.encoding='utf-8'
    savePage(url,res.text)
    soup=bs4.BeautifulSoup(res.text,'html.parser')
    for a_tag in soup.select('a'):
        next_url=str(a_tag.get('href'))
        isclear=1
        for inv in invalid_url_word:
            if not next_url.find(inv)==-1:
                isclear=0
                break
        if isclear:
            if not next_url in viewed_page:
                viewed_page.add(next_url)
                page_queue.append(next_url)

def savePage(url,text):
    pass

def start():
    return
    page_queue.append('')

    count=0
    while 1:
        if len(page_queue)==0:
            break
        url=page_queue[0]
        page_queue.pop(0)
        getPage(root_url+url)
        count+=1

if __name__=='__main__':
    start()
