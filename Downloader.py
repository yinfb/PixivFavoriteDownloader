import os
import requests
import re
import json


replace=False
DCount=0
PCount=0
PageNum=1

def LoadCookiesfromfile():
    jsona=json.loads(open('./Cookies.json').read())
    cookies=dict()
    for key in jsona:
        cookies[key['name']]=key['value']
    return cookies

def pximgdownload(FileName,imgurl):
    HttpHeader=dict()
    HttpHeader['Host']="i.pximg.net"
    HttpHeader['User-Agent']="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"
    HttpHeader['Accept']="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    HttpHeader['Accept-Language']="zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
    HttpHeader['Accept-Encoding']="gzip, deflate, br"
    HttpHeader['Connection']="keep-alive"
    HttpHeader['Upgrade-Insecure-Requests']="1"
    HttpHeader['Pragma']= "no-cache"
    HttpHeader['Cache-Control']="no-cache"
    HttpHeader['TE']="Trailers"
    HttpHeader['Referer']="https://app-api.pixiv.net/"
    IMGContent = requests.get(imgurl,stream=True,headers=HttpHeader)
    global DCount
    DCount +=1
    print(">>> %d / %d Downloading %s " % (PCount,DCount,FileName.split('./')[1]))
    if os.path.exists(FileName) and not replace:
        print("exist!")
        return False
    with open(FileName,'wb') as out_file:
        for chunk in IMGContent.iter_content(chunk_size=5120):
            if chunk:
                out_file.write(chunk)
    return True

def Download(pid):
    http=requests.Session()
    print("pid:%s"%(pid))
    Page=http.get('https://www.pixiv.net/artworks/'+str(pid),cookies=LoadCookiesfromfile())
    JsonStart=re.compile('<meta name="preload-data" id="meta-preload-data" content=\'')
    JsonEnd=re.compile('}}}\'')
    Error=re.compile('<h2 class="error-title">发生了错误</h2>')
    Error=Error.search(Page.text)
    if(not Error):
        jsonData=json.loads(Page.text[JsonStart.search(Page.text).end():JsonEnd.search(Page.text).end()-1])
        pageCount=jsonData["illust"][str(pid)]['pageCount']
        UrlPart=jsonData["illust"][str(pid)]['urls']['original'].split('p0')
        if(pageCount!=1):
            for pnumber in range(0,pageCount):
                
                Fullurl=UrlPart[0]+'p'+str(pnumber)+UrlPart[1]
                FileName='./'+str(pid)+'_p'+str(pnumber)+UrlPart[1]
                pximgdownload(FileName,Fullurl)
        else:
                Fullurl=jsonData["illust"][str(pid)]['urls']['original']
                url_basename = os.path.basename(Fullurl)
                extension = os.path.splitext(url_basename)[1]
                FileName='./'+str(pid)+extension
                pximgdownload(FileName,Fullurl)
    else:
        print("!!Error!!")

def Favoriteinfo():
    global PageNum
    baseurl="https://www.pixiv.net/bookmark.php?rest=show&p="
    http=requests.Session()
    
    while(PageNum):
        PageContent=http.get(baseurl+str(PageNum),cookies=LoadCookiesfromfile())
        pidSearch=re.compile('data-id="\d{1,}"')
        res=pidSearch.findall(PageContent.text)
        Pidset=set('')
        for ids in res:
            Pidset.add(str(ids.split('"')[1]))
        for id_ in Pidset:
            global PCount
            PCount+=1
            Download(id_)
        if(len(Pidset)<20):
            PageNum=0
        else:
            Pidset.clear()
            PageNum+=1
            print("----- %d -----"%(PageNum))

Favoriteinfo()