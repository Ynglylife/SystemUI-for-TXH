from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from pymongo import MongoClient
import re
import jieba
import jieba.analyse
import sys
import json
import os
from collections import Counter
import numpy
log = open('/home/seu/experiment/code/WeiBo/myProject/log', 'a+')
sys.path.append('/home/seu/experiment/code')
from result_extract import *

def logging(str):
    print(str)

def home_page(request):
    #return render(request,'index.html')
    return HttpResponseRedirect('/activity')
    #return render(request,'activity.html')

def activity(request):
    return render(request,'activity.html')

def message(request):
    return render(request,'message.html',{'datalist':None})

def cleanData(request):
    logging('cleaning data start')
    s=request.GET['cleanrule']
    s = s.strip().split('\r\n')
    if len(s) % 2 == 0:
        table = MongoClient().weibo.original
        total_count = table.find().count()
        k = 0
        for doc in table.find():
            k += 1
            if k % 10000 == 0:
                logging('已经清理%d%%' % (k * 100 / total_count))
            for i in range(0, len(s), 2):
                doc['text2'] = re.sub(s[i],s[i+1],doc['text2'])
            #table.update_one({'_id':doc['_id']}, {'$set':{'text2':doc['text2']}})
    logging('cleaning data complete')
    return HttpResponseRedirect('/activity')

def divideWord(request):
    logging('dividing data start')
    table = MongoClient().weibo.original
    total_count = table.find().count()
    k = 0
    for doc in table.find():
        seg = jieba.cut(doc['text2'])
        k += 1
        if k % 10000 == 0:
            logging('已经分割%d%%' % (k * 100 / total_count))
        #table.update_one({'_id': doc['_id']}, {'$set': {'text2_seg1': seg}})
    logging('dividing data complete')
    return HttpResponseRedirect('/activity')

def extractKeyword(request):
    logging('extracting keyword start')
    table = MongoClient().weibo.original
    total_count = table.find().count()
    k = 0
    for doc in table.find():
        keywords = jieba.analyse.extract_tags(doc['text2'], topK=10, withWeight=True)
        #table.update_one({'_id': doc['_id']}, {'$set': {'keywords': keywords}})
        k += 1
        if k % 10000 == 0:
            logging('已经提取%d%%' % (k * 100 / total_count))
    logging('extracting keyword complete')
    return HttpResponseRedirect('/activity')

def sentimentAnalysis(request):
    logging('sentiment analysis start')
    db = MongoClient().weibo
    original = db.original
    retweet = db.retweet
    total_count = original.find().count() + retweet.find().count()
    os.popen('/home/seu/experiment/code/SentimentAnalysis/a.out %d' & total_count)
    with open('/home/seu/experiment/data/sentiment_o') as oin:
        for line in oin.readlines():
            line = line.strip()
            if line:
                print(line)
                line = line.split()
                senti = line[1:]
                senti = [int(i.split('/'))[1] for i in senti]
                sp = sum(senti[:3])+senti[-1]-sum(senti[3:-1])
                # original.update_one({'_id': line[0]}, {'$set': {'polarity': sp>=0?1:0}})
    with open('/home/seu/experiment/data/sentiment_r') as oin:
        for line in oin.readlines():
            line = line.strip()
            if line:
                print(line)
                line = line.split()
                senti = line[1:]
                senti = [int(i.split('/'))[1] for i in senti]
                sp = sum(senti[:3])+senti[-1]-sum(senti[3:-1])
                # retweet.update_one({'_id': line[0]}, {'$set': {'polarity': sp>=0?1:0}})
    logging('sentiment analysis complete')
    return HttpResponseRedirect('/activity')

def topicAnalysis(request):
    role = request.GET['myrole']
    mintoken = request.GET['mintoken']
    minfre = request.GET['minfre']
    mindoc = request.GET['mindoc']
    model = request.GET['model']
    estniters = request.GET['estniters']
    ntopics = request.GET['ntopics']
    estalpha = request.GET['estalpha']
    estbeta = request.GET['estbeta']
    sys.path.append('/home/seu/experiment/code/WeiBo/weiboData')
    from generateDocument import GenerateDocument
    configfile = '/home/seu/experiment/code/WeiBo/weiboData/config.json'
    content = open(configfile,'r').read().strip()
    parms = json.loads(content)
    my_gen = GenerateDocument('weibo')
    if role == 'usr' and model == 'lda':
        logging('user topic analysis start')
        parms['generateTrain']['isusr'] = True
        #my_gen.generateRawData(**parms[my_gen.generateRawData.__name__])
        # os.popen('/home/seu/experiment/code/GibbsLDA++-0.2/src/lda \
        #         -est -alpha %f -beta %f -ntopics %d -niters %d -dfile /home/seu/experiment/data/inputdata/rawdata_usr'
        #          %(estalpha,estbeta,ntopics,estniters))
        logging('user topic analysis complete')
    elif role == 'blog' and model == 'lda':
        logging('blog topic analysis start')
        parms['generateTrain']['isusr'] = False
        #my_gen.generateRawData(**parms[my_gen.generateRawData.__name__])
        # os.popen('/home/seu/experiment/code/GibbsLDA++-0.2/src/lda \
        #         -est -alpha %f -beta %f -ntopics %d -niters %d -dfile /home/seu/experiment/data/inputdata/rawdata'
        #          %(estalpha,estbeta,ntopics,estniters))
        logging('blog topic analysis complete')
    elif role == 'usr' and model == 'hdp':
        logging('blog topic analysis start')
        parms['generateRawData']['isusr'] = True
        #my_gen.generateTrain(**parms[my_gen.generateTrain.__name__])
        # os.popen('/home/seu/experiment/code/hdp/hdp/hdp \
        #          --algorithm train --data /home/seu/experiment/data/inputdata/train --directory /home/seu/experiment/data/hdpsave --max_iter %d'
        #          %(estniters))
        logging('blog topic analysis complete')
    elif role == 'blog' and model == 'hdp':
        logging('blog topic analysis start')
        parms['generateRawData']['isusr'] = False
        #my_gen.generateTrain(**parms[my_gen.generateTrain.__name__])
        # os.popen('/home/seu/experiment/code/hdp/hdp/hdp \
        #          --algorithm train --data /home/seu/experiment/data/inputdata/train_usr --directory /home/seu/experiment/data/hdpsave --max_iter %d'
        #          %(estniters))
        logging('blog topic analysis complete')
    return HttpResponseRedirect('/activity')

def combine(request):
    logging('user vote merge start')
    tokennum = request.GET['tokennum']
    distance = request.GET['distance']
    logging('开始计算文本指纹')
    os.system('/home/seu/projects/text2hash/bin/x64/Release/text2hash.out %s' % tokennum)
    logging('开始对比文本指纹')
    os.system('/home/seu/projects/hamming_distamce/bin/x64/Release/hamming_distamce.out %s' % distance)
    logging('开始合并相同文本')
    table = MongoClient().weibo.first
    orgianl = MongoClient().weibo.original
    retweet = MongoClient().weibo.retweet
    data = {}
    orgianl_original = {}
    o_senti = {}
    for doc in orgianl.find():
        o_senti[doc['_id']] = doc['polarity']
    for doc in table.find():
        data[doc['_id']] = doc['created_time']
    with open('/home/seu/experiment/data/same_weibo') as input:
        for line in input.readlines():
            time = []
            print(line)
            line = line.strip().split()
            for id in line:
                time.append(data[id])
            zipped = zip(line,time)
            zipped = sorted(zipped,key=lambda x:x[1])
            for id in zipped:
                orgianl_original[id[0]] = zipped[0][0]
    #合并,考虑情感极性
    total_count = retweet.find().count()
    k=0
    for doc in retweet.find():
        k += 1
        if k % 10000 == 0:
            logging('已经处理%d%%' % (k * 100 / total_count))
        if doc['root'] in orgianl_original.keys():
            retweet.update_one({'_id':doc['_id']},{'$set':{'original_original':orgianl_original[doc['root']]}})
            if o_senti[doc['root']] != o_senti[orgianl_original[doc['root']]] and 'polarity' in doc.keys():
                retweet.update_one({'_id': doc['_id']}, {'$set': {'vote': 1-doc['polarity']}})
    logging('user vote merge complete')
    return HttpResponseRedirect('/activity')

def extractInput(request):
    logging('extract input data start')
    mininvolved = int(request.GET['mininvolved'])
    minretweet = int(request.GET['minretweet'])
    db = MongoClient().weibo
    mblogs ={}
    for i in db.first.find():
        mblogs[i['_id']] =[[i['uid'],1,0,0,i['created_time']]]

    for i in db.retweet.find():
        if 'vote' in i.keys():
            mblogs[i['original_original']].append([i['uid'], i['vote'], 0, 0, i['created_time']])
        else:
            mblogs[i['original_original']].append([i['uid'], 1, 0, 0, i['created_time']])

    for key in mblogs.keys():
        mblogs[key].sort(key=lambda x:x[4])
        c=0;
        for i in range(len(mblogs[key])):
            mblogs[key][i][2] = c
            mblogs[key][i][3] = i-c
            c+=mblogs[key][i][1]
        db.data.insert_one({'_id':key,'votes':mblogs[key]})

    top_topic = open('/home/seu/experiment/data/inputdata/top_topic').readlines()

    top_list = {}
    for i in top_topic:
        i = i.strip().split()
        top_list[i[0]] = [float(j.split(':')[0]) for j in i[1:]]

    dir = '/home/seu/experiment/data/gibbs/'
    print(0)
    all_reposts = []
    users = []
    mblog_id = []
    for repost in db.data.find(
            {'$and': [{'keywords': {'$exists': False}}, {'flag': 1}, {'novalue': {'$exists': False}}]}):
        if top_list[repost['_id']][0] > 0.2:
            mblog_id.append(repost['_id'])
            all_reposts.append(repost['votes'])
            users.extend([i[0] for i in repost['votes']])

    users_count = Counter(users)

    all_reposts = [[user[:-1] for user in repost if users_count[user[0]] > mininvolved] for repost in all_reposts]

    mblog_id = [mblog_id[i] for i in range(len(mblog_id)) if len(all_reposts[i]) > minretweet]

    all_reposts = [repost for repost in all_reposts if len(repost) > minretweet]

    with open(dir + 'mid', 'w') as mid:
        for i in mblog_id:
            mid.write(i + '\n')

    with open(dir + 'uid', 'w') as uid:
        uids = []
        for repost in all_reposts:
            uids.extend([i[0] for i in repost])
        users_count = Counter(uids)
        uids = list(set(uids))
        k = 0
        t = {}
        for i in uids:
            t[i] = k
            k += 1
            uid.write(i + '\n')

        for i in range(len(all_reposts)):
            for j in range(len(all_reposts[i])):
                all_reposts[i][j][0] = t[all_reposts[i][j][0]]

        with open(dir + 'data', 'w') as data:
            data.write('%d %d %d\n' % (len(all_reposts), len(uids), sum([len(repost) for repost in all_reposts])))
            for i in all_reposts:
                data.write('%d ' % len(i))
            data.write('\n')
            for i in uids:
                data.write('%d ' % users_count[i])
            for repost in all_reposts:
                for i in repost:
                    data.write('\n%d %d %d %d' % (i[0], i[1], i[2], i[3]))
    logging('extract input data complete')
    return HttpResponseRedirect('/message')

def solveElement(request):
    logging('estimate parameters start')
    niters = request.GET['niters']
    ntopics = request.GET['ntopics']
    alpha = request.GET['alpha']
    beta = request.GET['beta']
    gamma = request.GET['gamma']
    itard = request.GET['itard']
    tau = request.GET['tau']
    # os.popen('/home/seu/projects/gibbs_sampling/bin/x64/Release/gibbs_sampling.out %s %s %s %s %s %s %s' %
    #          (niters,ntopics,alpha,beta,gamma,itard,tau))
    logging('estimate parameters complete')
    return HttpResponseRedirect('/message')

def credibleBlogTop100(request):
    return render(request, 'message.html', {'datalist': get_t100blog()})

def credibleBlogButtom100(request):
    return render(request, 'message.html', {'datalist': get_b100blog()})

def conformableUsrTop100(request):
    return render(request, 'message.html', {'datalist': get_t100user()})

def conformableUsrButtom100(request):
    return render(request, 'message.html', {'datalist': get_b100user()})

def topicMasterTop100(request):
    return render(request,'message.html',{'datalist':get_expert()})
    #return HttpResponseRedirect('/message')
# Create your views here.
