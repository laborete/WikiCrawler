#!/usr/bin/env python
# coding: utf-8

# In[1]:


#要先install wikipedia 以及 wikipedia-api（用pip）
get_ipython().system('pip install wikipedia')
get_ipython().system('pip install wikipedia-api')
import wikipedia as wiki
import wikipediaapi as wikiapi
source = wikiapi.Wikipedia('zh-tw')

import numpy as np
import csv
import time
import random 

#總共要抓幾筆
target_sum = 10000
#這台機器上現在做好幾筆了，設定成0就好
current_sum = 0
#每看一百次query寫一次topic_exist和topic_queue檔
checkpoint = 0
#繁體中文
wiki.set_lang("zh-tw")

topic_exist = []
topic_queue = []

#拿好的摘要存進wiki.csv
filename = 'wiki.csv'


# In[3]:


# 一開始趕著弄，邏輯一塌糊塗，簡單來說是把exist（已經訪問過的），和queue（打算要訪問的）先load進來

topic_exist_tmp = []
topic_queue_tmp = []

with open('topic_exist.csv','r', encoding='utf-8') as csvfile:
    rows = csv.reader(csvfile)
    for row in rows:
        topic_exist_tmp.append(row)
with open('topic_queue.csv','r', encoding='utf-8') as csvfile:
    rows = csv.reader(csvfile)
    for row in rows:
        topic_queue_tmp.append(row)       

for item in topic_exist_tmp[0]:
    topic_exist.append(item)
for item in topic_queue_tmp[0]:
    topic_queue.append(item)
#其他機器在跑其他位置的queue，每次訪問會補queue，所以topic_queue選其中一小部分就好，他會自己變多，不超過一百萬
queue_head = random.randint(1,500000)
topic_queue = topic_queue[queue_head:]
current_sum = 0


# In[4]:


def upload(filename,data):
    with open(filename,'a', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(data)

def workingfile_upload(filename,data):
    with open(filename,'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(data)


# In[5]:


while(current_sum < target_sum):
    #read page
    print('checking',topic_queue[0],'...')
    page = source.page(topic_queue[0])
    checkpoint = checkpoint+1
    #if the page exists and we have not copied it yet, copy it
    if page.exists() and topic_queue[0] not in topic_exist:
        topic_exist.append(topic_queue[0])
        #sometimes it doesn't work because of language or redirection issues
        try:
            page_en = page.langlinks['en']
            upload('wiki.csv',[page.title,page.summary[:],page_en.title,page_en.summary[:]])
            if(len(topic_queue)<1000000):
                for title in page.links.keys():
                    topic_queue.append(title)
            current_sum = current_sum + 1
        except:
            print('something went wrong copying',topic_queue[0])
    else:
        print(topic_queue[0],'Not Found or Already Exist')
    
    if checkpoint%100==0:
        try:
            workingfile_upload('topic_exist.csv',topic_exist)
            workingfile_upload('topic_queue.csv',topic_queue)
        except:
            print('failed to save topic_exist or topic_queue')
        print('Amount of topics saved:',current_sum)
    #丟掉用過的queue
    del topic_queue[0]
    #應該不會發生queue用完的悲劇啦
    if len(topic_queue) == 0:
        print('Oops, no topic left!')
        break
#維基伺服器一段時間就會讓我timeout（可能是八小時之類），應該是做不完，做多少算多少，程序死了之後直接再跑一次即可    
print('Done,',current_sum,'topics are saved.') 

