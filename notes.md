最近在抓取网易云音乐的数据，云村的数据抓取不需要登录认证，但是有些动态加载的数据需要post浏览器端加密过的数据。比如用户的playlist，和rank排行，歌曲的评论信息。这些数据都需要向http://music.163.com/weapi/v1/-/?csrf_token=发送带加密数据params和encSecKey post请求。

下面以听歌排行榜抓去为例说明如何抓取需要的数据

![](http://o6z0iouhm.bkt.clouddn.com/Fi8uZ5YGp1XyUrhYRNDlzwuY1vUr)

打开检查network并再次点击最近一周触发

![](http://o6z0iouhm.bkt.clouddn.com/Fiw7bF6plv7iRCPwGNkS3Dzy9_Xn)

产生http://music.163.com/weapi/v1/play/record?csrf_token=

对应参数params，encSecKey

![](http://o6z0iouhm.bkt.clouddn.com/FmByE2-PRUAGyRDxpAkr_U1-fM19)

params其实是由一个json字符串，经过2轮AES加密得到的，第一轮的密钥是固定的16位字符串，第二轮的密钥是随机的16位字符串，而encSecKey就是第二轮的密钥RSA加密后的结果

Initiator为core.js

搜索formatted的core.js 得到

<img src="http://o6z0iouhm.bkt.clouddn.com/FibdD4tluG4uVRzxg5eUyjWW3U6p" style="zoom:50%">

上面的函数点是关键的加密方法，设置函数d的断点，重新点击页面触发，得到如下参数

![](http://o6z0iouhm.bkt.clouddn.com/FimdPlTj0h5u7jo_TiEqZkfjYX72)

d为需要加密的json数据，不同的请求对应不同的数据，e,f,g 都是固定的

encSecKey 由 参数i,e,f产生，e，f是固定的，我们将i以后都固定成"**FFFFFFFFFFFFFFFF**",得到固定的encSecKey

![](http://o6z0iouhm.bkt.clouddn.com/Ftdm8QkWmXVDPJzrHWOC0QiZ2oG1)

将上述的js加密方法写成python版本如下

```python
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
```






### 参考资料

> https://www.zhihu.com/question/36081767