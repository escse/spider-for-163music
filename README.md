# spider-for-163music
网易云音乐抓去用户，歌单，评论
目标是

需要抓取的任务有
1. 用户 user
2. 用户的听歌排行榜 record
3. 歌单 playlist
4. 歌曲
5. 歌曲中的评论

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