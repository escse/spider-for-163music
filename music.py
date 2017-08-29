#coding:utf8
import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
import base64, json
import threading, time
from multiprocessing.pool import ThreadPool

root = "http://music.163.com/"
s = requests.session()
threadsNum = 50 # change as you like , better not too large
limits = 100 
headers = {
    'Cookie': 'appver=1.5.0.75771;',
    'Referer': 'http://music.163.com/'
}

class Encrypt:
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    # the following two are used for encSecKey, but it's a constant now
    # second_param = "010001"
    # third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    first_key = "0CoJUm6Qyw8W8jud" # forth_param
    second_key = 16 * 'F'
    iv = "0102030405060708"

    def __init__(self):
        self.cache = dict()

    def encrypt_params(self, s):
        encrypt_text = self.AES_encrypt(s, self.first_key, self.iv)
        encrypt_text = self.AES_encrypt(encrypt_text, self.second_key, self.iv)
        return encrypt_text
    
    def decrypt_params(self, s):
        decrypt_text = self.AES_encrypt(s, self.second_key, self.iv)
        encrypt_text = self.AES_encrypt(decrypt_text, self.first_key, self.iv)
        return encrypt_text

    def AES_encrypt(self, text, key, iv):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypt_text = encryptor.encrypt(text)
        encrypt_text = base64.b64encode(encrypt_text)
        return encrypt_text
    
    def AES_decrypt(self, text, key, iv):
        decrypt_text = base64.b64decode(text)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        decrypt_text = encryptor.decrypt(decrypt_text)
        pad = ord(decrypt_text[-1])
        if all([t==decrypt_text[-1] for t in decrypt_text[-pad:]]):
            decrypt_text = decrypt_text[:-pad]
        return decrypt_text

    def get(self, s):
        if s not in self.cache:
            self.cache[s] = self.encrypt_params(s)
        return  {"params": self.cache[s],
                 "encSecKey": self.encSecKey
                }


def getjson(name, *argv):
    if name == "comment":
        limits = 100
        offset = argv[0]
        return '{{rid:"", offset:"{}", total:"{}", limit:"{}", csrf_token:""}}'.format(limits * offset, "true" if offset == 0 else "false", limits)
    if name == "record":
        uid = argv[0]
        if argv[1] == "week":
            _type = 1
        elif argv[1] == "year":
            _type = 0
        else:
            _type = 0
        return '{{"uid":"{}", "type":"{}", "limit":"1000", "offset":"0", "total":"true", "csrf_token":""}}'.format(uid, _type)
    if name == "playlist":
        uid = argv[0]
        return '{{"uid":"{}","type":"-1","limit":"1000","offset":"0","total":"true","csrf_token":""}}"'.format(uid)

encrypt = Encrypt()
    
class song:
    def __init__(self, sid, name=None):
        self.name = name
        self.id = sid
        url = root + "song?id=" + str(id)
        self.comments = None
        # html = requests.get(url).text
        # self.soup = BeautifulSoup(html, 'html.parser')
    

    def getComment(self):
        #   data key:
        #       isMusician    code   userId  hotComments comments    
        #       more    topComments total   moreHot
        #   comment key:
        #       liked   beReplied   content* user
        #       likedCount  time    commentId
        #  user key:
        #       avatarUrl   expertTags  remarkName  userId*
        #       locationInfo    userType    experts authStatus
        #       nicknamevipType
        def task(argv):
            comments, url, i = argv
            response = s.post(url, headers=headers, data=encrypt.get(getjson("comment", i)))
            data = json.loads(response.content)
            comments.extend(data["comments"])
        url = root + "weapi/v1/resource/comments/R_SO_4_{}/?csrf_token=".format(self.id)
        response = s.post(url, data=encrypt.get(getjson("comment", 0)))
        if response.status_code == 503:
            print(response)
            print("Template unavailable, wait...")
            exit(0)
        data = json.loads(response.content)
        self.comments = data["comments"]
        # hotComments = data["hotComments"]
        num = int(data["total"])   # comments num
        print(u"Song {name} id = {id} has {num} comments".format(name=self.name, id=self.id, num=num))
        workers = ThreadPool(threadsNum)
        workers.map(task, [(self.comments, url, i) for i in range((num - 1) / limits + 1)])
    
    def searchUserId(self, uid):
        if not self.comments:
            self.getComment()
        for c in self.comments:
            if c["user"]["userId"] == uid:
                print(c["content"].encode("utf8"))


class playlist:
    def __init__(self, pid):
        url = root + "playlist?id=" + str(pid)
        html = s.get(url, headers=headers).content
        soup = BeautifulSoup(html, 'html.parser')
        songs = soup.find(id="song-list-pre-cache").find_all("li") #TODO sometimes no songs return only template
        # songs = soup.find('ul',{'class':'f-hide'})
        self.songs = [song(li.a["href"].split("=")[1], li.string) for li in songs]
        self.soup = soup
    
    def searchUserId(self, uid):
        for s in self.songs:
            s.searchUserId(uid)
    
    def __len__(self):
        return len(self.songs)

class user:
    def __init__(self, uid):
        self.id = str(uid)
        url = root + "user?id=" + self.id
        html = s.get(url, headers=headers).text
        # print html.encode("utf8")
        soup = BeautifulSoup(html, 'html.parser')
        self.name = soup.find(id="j-name-wrap").span.string
        self.soup = soup
        self.monitorDict = None
        url = root + "weapi/user/playlist?csrf_token="
        response = s.post(url, headers=headers, data=encrypt.get(getjson("playlist", self.id)))        
        data = json.loads(response.content)
        self.playlists = [d["id"] for d in data["playlist"]]
        
    
    def getRecord(self, name="week", log=True):
        # year: allData
        # week: weekData
        #   a list: playCount, score, song
        #       song: name, id ..
        url = root + "weapi/v1/play/record?csrf_token="
        response = s.post(url, headers=headers, data=encrypt.get(getjson("record", self.id, name)))
        if name == "week":
            key = "weekData"
        else:
            key = "allData"
        data = json.loads(response.content)[key]
        if log:
            for i, item in enumerate(data):
                song = item["song"]
                print(u"rank {rank} score = {score} {name} id= {id}".format(rank=i+1, score=item["score"], name=song["name"], id=song["id"]))
        return data

    def organize(self, data):
        return {d["song"]["id"]: [d["song"]["name"], d["score"]] for d in data}

    def monitor(self, name="week"):
        while 1:
            data = self.getRecord(name=name, log=False)
            if self.monitorDict:
                flag = 0
                for d in data:
                    sid = d["song"]["id"]
                    if sid in self.monitorDict:
                        if self.monitorDict[sid][1] != d["score"]:
                            flag += 1
                            addScore =  d["score"] - self.monitorDict[sid][1]
                            print(u"Song {name} has been played for another {t} times".format(name=d["song"]["name"], t=addScore))
                    if sid not in self.monitorDict:
                        flag += 1
                        addScore = d["score"]
                        print(u"Song {name} has been played for another {t} times".format(name=d["song"]["name"], t=addScore))
                if flag == 0:
                    print("No update since last time")
            self.monitorDict = self.organize(data)
            time.sleep(10)