#coding:utf8
import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
import base64, json

userid = 304193210
homepage = "http://music.163.com/#/user/home?id={}".format(userid)
ranklist = "http://music.163.com/#/user/songs/rank?id={}".format(782188957)

root = "http://music.163.com/"
limits = 100
s = requests.session()

class encrypt:
    # offset 和 limits 控制评论
    # [offset, offset + limits)
    cache = dict()
    
    @staticmethod
    def get_params(offset):
        #######
        first_param = '{{rid:"", offset:"{}", total:"{}", limit:"{}", csrf_token:""}}'.format(limits * offset, "true" if offset == 0 else "false", limits)
        second_param = "010001"
        third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        forth_param = "0CoJUm6Qyw8W8jud"
        #######
        iv = "0102030405060708"
        first_key = forth_param
        second_key = 16 * 'F'
        h_encText = encrypt.AES_encrypt(first_param, first_key, iv)
        h_encText = encrypt.AES_encrypt(h_encText, second_key, iv)
        return h_encText
    
    @staticmethod
    def get_encSecKey():
        encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
        return encSecKey
    
    @staticmethod
    def AES_encrypt(text, key, iv):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypt_text = encryptor.encrypt(text)
        encrypt_text = base64.b64encode(encrypt_text)
        return encrypt_text

    @staticmethod
    def data(offset):
        if str(offset) not in encrypt.cache:
            d = {
                "params": encrypt.get_params(offset),
                "encSecKey": encrypt.get_encSecKey()
            }
            encrypt.cache[str(offset)] = d
        return encrypt.cache[str(offset)]

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
        #   user key:
        #       avatarUrl   expertTags  remarkName  userId*
        #       locationInfo    userType    experts authStatus
        #       nicknamevipType

        url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_{}/?csrf_token=".format(self.id)
        response = s.post(url, data=encrypt.data(0))
        data = json.loads(response.content)
        comments = data["comments"]
        # hotComments = data["hotComments"]
        num = int(data["total"])   # 评论数
        print(u"Song {name} id = {id} has {num} comments".format(name=self.name, id=self.id, num=num))
        for i in range((num - 1) / limits + 1):
            response = s.post(url, data=encrypt.data(i+1))
            data = json.loads(response.content)
            comments.extend(data["comments"])
        self.comments = comments
    
    def searchUserId(self, uid):
        if not self.comments:
            self.getComment()
        for c in self.comments:
            if c["user"]["userId"] == uid:
                print(c["content"].encode("utf8"))


class playlist:
    def __init__(self, pid):
        headers = { 'Referer':'http://music.163.com/', 'Host':'music.163.com', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.3.0', 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }
        url = root + "playlist?id=" + str(pid)
        html = s.get(url, headers=headers).content
        soup = BeautifulSoup(html, 'html.parser')
        songs = soup.find(id="song-list-pre-cache").find_all("li")
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
        html = s.get(url).text
        print html.encode("utf8")
        soup = BeautifulSoup(html, 'html.parser')
        self.name = soup.find(id="j-name-wrap").span.string
        self.soup = soup
        url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_{}/?csrf_token=".format(self.id)
        response = s.post(url, data=encrypt.data(0))
        data = json.loads(response.content)
        # self.playlists = 
        # http://music.163.com/weapi/v1/play/record?csrf_token=
        # http://music.163.com/weapi/user/playlist?csrf_token=
# songid = [234267, 298894]
userid = [304193210, 36419305]
playlistid = [422051335, 648764947, 644137792, 642036961, 508154476]
# user(userid[1])
# song(songid).searchUserId(88781991)
# song(298894).searchUserId(88781991)
# 参考资料 https://www.zhihu.com/question/36081767 
# https://www.zhihu.com/question/41505181?sort=created
for pid in playlistid:
    playlist(pid).searchUserId(userid[0])