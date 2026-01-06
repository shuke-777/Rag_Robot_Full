# Linux 命令行基础教程

## 1. Linux 简介

Linux 是一个开源的类Unix操作系统内核，广泛应用于服务器、嵌入式设备和超级计算机。

### 1.1 常见Linux发行版

- **Ubuntu**: 适合初学者
- **CentOS/RHEL**: 企业级服务器
- **Debian**: 稳定性好
- **Arch Linux**: 高度定制化

## 2. 文件系统结构

```
/              根目录
├── /bin       基本命令二进制文件
├── /etc       配置文件
├── /home      用户主目录
├── /usr       用户程序
├── /var       可变数据（日志等）
├── /tmp       临时文件
└── /opt       可选应用程序
```

## 3. 基础命令

### 3.1 文件和目录操作

```bash
# 查看当前目录
pwd

# 列出文件
ls
ls -l      # 详细信息
ls -la     # 包含隐藏文件
ls -lh     # 人类可读的文件大小

# 切换目录
cd /path/to/directory
cd ~       # 回到主目录
cd ..      # 上一级目录
cd -       # 返回上一个目录

# 创建目录
mkdir dirname
mkdir -p path/to/dirname  # 创建多级目录

# 删除目录
rmdir dirname              # 只能删除空目录
rm -r dirname              # 递归删除
rm -rf dirname             # 强制递归删除（危险！）

# 复制文件/目录
cp file1 file2
cp -r dir1 dir2           # 复制目录

# 移动/重命名文件
mv file1 file2
mv file1 /path/to/        # 移动文件

# 删除文件
rm file
rm -f file                # 强制删除

# 创建空文件或更新时间戳
touch file.txt

# 查看文件内容
cat file.txt              # 显示全部内容
less file.txt             # 分页查看
head file.txt             # 查看前10行
head -n 20 file.txt       # 查看前20行
tail file.txt             # 查看后10行
tail -f file.txt          # 实时查看文件更新
```

### 3.2 文件搜索

```bash
# 查找文件
find /path -name "*.txt"
find . -type f -name "*.py"
find . -type d -name "test*"

# 按大小查找
find . -size +100M        # 大于100MB
find . -size -1M          # 小于1MB

# 按时间查找
find . -mtime -7          # 最近7天修改的文件

# 搜索文件内容
grep "pattern" file.txt
grep -r "pattern" .       # 递归搜索
grep -i "pattern" file    # 忽略大小写
grep -n "pattern" file    # 显示行号
```

## 4. 文件权限

### 4.1 权限表示

```bash
# 权限格式：drwxrwxrwx
# d: 目录  -: 文件  l: 链接
# rwx: 读(4) 写(2) 执行(1)
# 三组：所有者 组 其他人

# 查看权限
ls -l file.txt
# -rw-r--r-- 1 user group 1234 Jan 01 10:00 file.txt
```

### 4.2 修改权限

```bash
# 数字方式
chmod 755 file.txt        # rwxr-xr-x
chmod 644 file.txt        # rw-r--r--

# 符号方式
chmod u+x file.txt        # 所有者添加执行权限
chmod g-w file.txt        # 组删除写权限
chmod o=r file.txt        # 其他人只有读权限
chmod a+x file.txt        # 所有人添加执行权限

# 修改所有者
sudo chown user file.txt
sudo chown user:group file.txt

# 递归修改
chmod -R 755 directory/
```

## 5. 进程管理

### 5.1 进程查看

```bash
# 查看进程
ps
ps aux                   # 查看所有进程
ps aux | grep python     # 查找特定进程

# 实时进程监控
top
htop                     # 更友好的界面（需要安装）

# 查看进程树
pstree
```

### 5.2 进程控制

```bash
# 后台运行
python script.py &

# 查看后台任务
jobs

# 将后台任务调到前台
fg %1

# 将前台任务放到后台
Ctrl+Z                   # 暂停任务
bg %1                    # 在后台继续运行

# 杀死进程
kill PID
kill -9 PID              # 强制杀死
killall process_name     # 杀死所有同名进程
```

## 6. 网络命令

```bash
# 测试网络连接
ping google.com
ping -c 4 google.com     # 只ping 4次

# 查看网络接口
ifconfig                 # 老命令
ip addr show             # 新命令

# 查看端口占用
netstat -tuln
lsof -i :8000            # 查看8000端口

# 下载文件
wget https://example.com/file.zip
curl -O https://example.com/file.zip

# SSH 远程连接
ssh user@hostname
ssh user@192.168.1.100

# 传输文件
scp file.txt user@host:/path/
scp -r dir/ user@host:/path/
```

## 7. 文本处理

### 7.1 文本编辑

```bash
# nano编辑器（简单）
nano file.txt

# vim编辑器（强大）
vim file.txt
# i: 进入插入模式
# Esc: 退出插入模式
# :w: 保存
# :q: 退出
# :wq: 保存并退出
# :q!: 不保存退出
```

### 7.2 文本处理工具

```bash
# 统计行数、字数
wc file.txt
wc -l file.txt           # 只统计行数

# 排序
sort file.txt
sort -n file.txt         # 数字排序
sort -r file.txt         # 逆序

# 去重
uniq file.txt
sort file.txt | uniq     # 先排序再去重

# 替换
sed 's/old/new/g' file.txt              # 显示替换结果
sed -i 's/old/new/g' file.txt           # 直接修改文件

# 提取列
cut -d ',' -f 1 file.csv                # 提取CSV第1列
awk '{print $1}' file.txt               # 打印第1列
```

## 8. 管道和重定向

### 8.1 重定向

```bash
# 输出重定向
echo "hello" > file.txt              # 覆盖写入
echo "world" >> file.txt             # 追加写入

# 错误重定向
command 2> error.log                 # 错误输出到文件
command &> all.log                   # 标准输出和错误都重定向

# 输入重定向
command < input.txt
```

### 8.2 管道

```bash
# 将一个命令的输出作为另一个命令的输入
ls -l | grep ".txt"
ps aux | grep python | wc -l
cat file.txt | sort | uniq | wc -l
```

## 9. 压缩和解压

```bash
# tar归档
tar -cvf archive.tar files/          # 创建归档
tar -xvf archive.tar                 # 解包
tar -tvf archive.tar                 # 查看内容

# gzip压缩
tar -czvf archive.tar.gz files/      # 创建压缩归档
tar -xzvf archive.tar.gz             # 解压

# zip压缩
zip archive.zip file1 file2
zip -r archive.zip directory/        # 递归压缩
unzip archive.zip                    # 解压
```

## 10. 系统信息

```bash
# 系统信息
uname -a                 # 系统信息
lsb_release -a           # Linux发行版信息
hostname                 # 主机名

# 磁盘使用情况
df -h                    # 磁盘空间
du -sh directory/        # 目录大小
du -h --max-depth=1 .    # 当前目录各子目录大小

# 内存使用情况
free -h

# CPU信息
lscpu
cat /proc/cpuinfo

# 查看正在运行的服务
systemctl list-units --type=service
systemctl status nginx
```

## 11. 软件包管理

### 11.1 Debian/Ubuntu (apt)

```bash
# 更新包索引
sudo apt update

# 升级所有包
sudo apt upgrade

# 安装软件
sudo apt install package_name

# 删除软件
sudo apt remove package_name
sudo apt purge package_name          # 同时删除配置文件

# 搜索软件包
apt search keyword

# 查看已安装的包
apt list --installed
```

### 11.2 CentOS/RHEL (yum/dnf)

```bash
# 更新系统
sudo yum update

# 安装软件
sudo yum install package_name

# 删除软件
sudo yum remove package_name

# 搜索软件包
yum search keyword
```

## 12. 环境变量

```bash
# 查看环境变量
env
echo $PATH
echo $HOME

# 临时设置
export MY_VAR="value"

# 永久设置（添加到 ~/.bashrc 或 ~/.bash_profile）
echo 'export MY_VAR="value"' >> ~/.bashrc
source ~/.bashrc            # 重新加载配置

# 查看PATH
echo $PATH

# 添加到PATH
export PATH=$PATH:/new/path
```

## 13. 常用快捷键

```bash
Ctrl+C              # 中断当前命令
Ctrl+D              # 退出当前Shell
Ctrl+Z              # 暂停当前命令
Ctrl+L              # 清屏
Ctrl+A              # 移到行首
Ctrl+E              # 移到行尾
Ctrl+U              # 删除光标前的内容
Ctrl+K              # 删除光标后的内容
Ctrl+R              # 搜索历史命令
Tab                 # 自动补全
↑/↓                 # 浏览历史命令
```

## 14. Shell 脚本基础

### 14.1 创建脚本

```bash
#!/bin/bash
# 这是一个简单的Shell脚本

echo "Hello, World!"

# 变量
NAME="Alice"
echo "Hello, $NAME"

# 条件判断
if [ -f "file.txt" ]; then
    echo "文件存在"
else
    echo "文件不存在"
fi

# 循环
for i in 1 2 3 4 5; do
    echo "Number: $i"
done

# 函数
greet() {
    echo "Hello, $1!"
}

greet "Bob"
```

### 14.2 运行脚本

```bash
# 添加执行权限
chmod +x script.sh

# 运行脚本
./script.sh
bash script.sh
```

## 15. 实用技巧

### 15.1 命令别名

```bash
# 临时别名
alias ll='ls -la'
alias gs='git status'

# 永久别名（添加到 ~/.bashrc）
echo "alias ll='ls -la'" >> ~/.bashrc
```

### 15.2 查看命令历史

```bash
# 查看历史
history

# 执行历史命令
!100                # 执行第100条命令
!!                  # 执行上一条命令
!ls                 # 执行最近的ls命令
```

### 15.3 文件链接

```bash
# 硬链接
ln source.txt link.txt

# 软链接（符号链接）
ln -s /path/to/source.txt link.txt
```

## 16. 常见问题解决

### 16.1 权限不足

```bash
# 使用sudo提升权限
sudo command

# 切换到root用户（不推荐）
sudo su -
```

### 16.2 查找大文件

```bash
# 查找大于100MB的文件
find / -type f -size +100M 2>/dev/null

# 查找最大的10个文件
du -ah / 2>/dev/null | sort -rh | head -n 10
```

### 16.3 清理磁盘空间

```bash
# 清理包缓存（Ubuntu）
sudo apt clean
sudo apt autoremove

# 清理日志
sudo journalctl --vacuum-time=7d

# 清理临时文件
sudo rm -rf /tmp/*
```

## 总结

Linux命令行是开发者必备技能：
- **文件操作**: ls, cd, mkdir, cp, mv, rm
- **文件查看**: cat, less, head, tail, grep
- **权限管理**: chmod, chown
- **进程管理**: ps, top, kill
- **网络命令**: ping, ssh, scp, wget
- **文本处理**: grep, sed, awk, sort
- **系统管理**: systemctl, apt, yum

熟练掌握这些命令可以大大提高工作效率！
