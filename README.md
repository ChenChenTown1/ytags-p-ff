![logo](https://github.com/ChenChenTown1/ytags-p-ff/blob/main/image/icon.png?raw=true)
# **ytags-p-ff**
stands for: youtube auto generated subs paraphraser for ffmpeg
### 记得star, 支持下

## 介绍:
这是一个能让你用yt-dlp下载好youtube自动生成的字幕(.srt)后给字幕时间轴重组, 这样可以让你用ffmpeg嵌入硬字幕的时候可以只有一行. 软字幕的话还没测试过(理论上可行).
*这个是我遇到的问题, 我开发的解决方案.*

## 要求
##### python ≥ 3.0
##### ffmpeg 都行 (我用的是8.0.1)
##### curl 都行
##### wget 都行
##### 视频必须要是mp4, 字幕必须要是srt. (在用yt-dlp下载的时候都可以自定义)
##### 要能执行sh文件就行

## 使用方式:
无需下载
##### 1.先cd到需要处理的文件夹
##### 2.执行此命令来处理.srt文件:
    curl -s https://raw.githubusercontent.com/ChenChenTown1/ytags-p-ff/refs/heads/main/fix_srt.py | python3 -

##### 3.等待处理完毕, 带有_fixed是处理完的
##### 4.处理完字幕后, 要删除字幕文件名里的语言后缀(比如.en), 用这个命令:
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ChenChenTown1/ytags-p-ff/refs/heads/main/remove_langs_codes.sh)" || sh -c "$(wget -qO- https://raw.githubusercontent.com/ChenChenTown1/ytags-p-ff/refs/heads/main/remove_langs_codes.sh)"

##### 5.还需删除字幕文件名里的youtube编号, 就是在[]里的一串字母
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ChenChenTown1/ytags-p-ff/refs/heads/main/remove_youtube_number.sh)" || sh -c "$(wget -qO- https://raw.githubusercontent.com/ChenChenTown1/ytags-p-ff/refs/heads/main/remove_youtube_number.sh)"

##### 用这个脚本进行合成(它会把名字最像的和带有_fixed的文件用ffmpeg合成):
    curl -s https://raw.githubusercontent.com/ChenChenTown1/ytags-p-ff/refs/heads/main/embed_subs.py | python3 -



## Star History

<a href="https://www.star-history.com/#ChenChenTown1/ysiol-ec&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ChenChenTown1/ysiol-ec&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ChenChenTown1/ysiol-ec&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ChenChenTown1/ysiol-ec&type=date&legend=top-left" />
 </picture>
</a>
