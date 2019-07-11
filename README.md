# axe
python expect ssh 

适用于多个服务器用户名密码相同的情况下。

修改axe文件
```
USER = 'root'
PASSWORD = 'root'
PORT = '22'
```
添加alias
```
alias axe='/Users/axe/.axe/axe'
```
参考如下文档使用
```
help:
axe 1 ==> ssh root@192.222.1.1 (use root password of astute)
axe 10.10.1.1 ==> ssh root@10.10.1.1 (use root password of astute)
axe 2 3 4 -c 'ls -lrt' ==> run command on host002/3/4 and show result
axe 2 3 4 -s './test' '/home/astute' ==> scp file to host002/3/4 on purpose
axe 2 3 4 -s './test' ==> scp file to host002/3/4 to the same place
```
