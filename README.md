# spider-for-163music
网易云音乐抓取用户，歌单，评论

需要抓取的任务有
1. 用户 user
2. 用户的听歌排行榜 record
3. 歌单 playlist
4. 歌曲
5. 歌曲中的评论

### 说明
[说明.md](./notes.md)

### Example

从歌曲中搜索用户评论
```
s = song(443008) # 以id创建一首歌的instance
s.searchUserId(36419305) # 搜索该id的用户
```

从歌单中搜索所有歌曲中用户的评论
```
p = playlist(35547018) # 以id创建一个歌单的instance
p.searchUserId(36419305) # 搜索该id的用户
```



### Done
- [x] 从用户主页抓取歌单
- [x] 从歌单中抓取歌曲
- [x] 从歌曲中抓取评论
- [x] 从评论中搜索用户
- [x] 评论抓取多线程

### TODO
- [ ] 增加应对后台检测的方法
- [ ] 扩展多线程，并改进成协程
- [ ] 优化代码

### 参考资料
1. https://www.zhihu.com/question/36081767 
2. https://www.zhihu.com/question/41505181