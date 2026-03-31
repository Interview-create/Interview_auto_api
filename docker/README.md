# 自動化測試 docker image

因應測試需求，以 rel 環境的 db base 做為測試基底，並在需時定期更新

## image 存放專案
- [automation/automation](https://a.com/harbor/projects/138/repositories/automation)
- [automation/oracle](https://a.com/harbor/projects/138/repositories/oracle)
- [automation/mysql](https://a.com/harbor/projects/138/repositories/mysql)

---

## 使用指南

用以下指令來建立實體(以 oracle 為例)
```
docker run -d --name ${ap_name} -p ${custom_port}:1521 a.com/automation/oracle:latest
```

- ap_name: 為 docker 容器名稱
- custom_port: 對外要接的 port

### 常見疑難
剛執行時會需要一點時間完整啟動，之後 port 才能打通

可透過以下指令確認對應 port 是否開放
```
netstat -tulpn | grep -v tcp6 | grep LISTEN | grep :${custom_port} | awk '{print $7}'
```

---

## 更新 base image

### 前置準備(放置在要用來打包的伺服器上)
- rel 環境的 dmp 備份檔
- 這個專案內附的更新腳本(以更新 oracle / mysql 分為兩種)

## 以更新 oracledb image 為例

更新腳本 `/tmp/update_rel_oracle_database.sh`
<pre>
root@dev-dt-backendrv02(03:02:31)[/tmp]$ ls -l
total 4
-rwxr-xr-x 1 root   root   3885 Feb 10 11:43 update_rel_oracle_database.sh*
</pre>

備份檔 `/u02/db_imp_dir/`
<pre>
root@dev-dt-backendrv02(03:03:50)[/tmp]$ l /u02/db_imp_dir/
total 790M
151995037 drwxr-xr-x 2 root root   40 Feb  7 15:05 ./
142960211 drwxr-xr-x 3 root root   23 Feb  7 15:02 ../
 19001696 -rw-r--r-- 1 root root 790M Feb  2 16:36 bk_rel-dt-mgmt_20230201.dmp
</pre>

執行腳本，參數帶備份檔案的 **絕對路徑**

```
./update_rel_oracle_database.sh /u02/db_imp_dir/bk_rel-dt-mgmt_20230201.dmp
```

腳本會對 harbor repo 推送 latest 標籤為最新版本
