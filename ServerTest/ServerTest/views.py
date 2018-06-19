#coding=utf-8

from django.http import HttpResponse
from django.shortcuts import render
import jieba
import MySQLdb
import json

class Page():
    def __init__(self,id,url,title,text,pr):
        self.id=id
        self.url=url
        self.title=title
        self.text=text
        self.pr=pr
    def getpoint(self,query_list):
        score=0
        text_list=set(self.text.split(' '))
        for query in query_list:
            if self.title.find(query)>-1:
                score+=100
            if query in text_list:
                score+=1
        score+=self.pr*10
        return score

db = MySQLdb.connect("localhost", "root", "", "irtest", charset='utf8')
cursor = db.cursor()

def hello(request):
    context= {}
    context['hello'] = 'Hello World!'
    return render(request, 'main.html', context)

def search(request):
    rlist=request.GET
    text=''
    page=0
    result_per_page=10

    if 'text' in rlist:
        text=rlist['text']
    if 'page' in rlist:
        page=int(rlist['page'])

    seg_list = jieba.cut_for_search(text)
    seg_list=list(set(seg_list))

    str_sql=map(lambda x:'\''+x+'\'',seg_list)
    str_sql=reduce(lambda x,y:x+','+y,str_sql)
    str_sql="select page_id from word where word in ("+str_sql+")"

    cursor.execute(str_sql)
    results = cursor.fetchall()

    page_list=[]
    for row in results:
        page_list.extend(row[0].split(' '))
    page_list=list(set(page_list))

    if len(page_list)==0:
        return HttpResponse("{'num':0}")

    str_sql=reduce(lambda x,y:x+','+y,map(str,page_list))
    str_sql2=str_sql
    str_sql="select id,url,title,text,pr from page where id in ("+str_sql+")"

    cursor.execute(str_sql)
    results = cursor.fetchall()

    page_map={}
    score={}
    for row in results:
        page_map[row[0]]=Page(row[0],row[1],row[2],row[3],row[4])
        score[row[0]]=page_map[row[0]].getpoint(seg_list)

    items = score.items() 
    items.sort(key=lambda x:x[1],reverse=True) 
    score= [key for key, value in items] 

    ret_list=None
    if (page+1)*result_per_page>len(score):
        ret_list=score[page*result_per_page:]
    else:
        ret_list=score[page*result_per_page:(page+1)*result_per_page]
        
    dic_list=[]
    for page_id in ret_list:
        page_obj=page_map[page_id]
        dic_list.append({'url':page_obj.url,'title':page_obj.title,'text':page_obj.text})
    
    str_sql="select count(*) from page where id in ("+str_sql2+")"

    cursor.execute(str_sql)
    results = cursor.fetchall()

    ret_dic={'num':results[0][0],'list':dic_list}
    
    json_obj=json.dumps(ret_dic)

    return HttpResponse(json_obj)