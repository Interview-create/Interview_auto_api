#!/bin/bash

# 參數
base_db_file=$1

docker_app=rel_database_isolation
pump_dir="$(dirname "${base_db_file}")"
pump_file="$(basename "${base_db_file}")"
log_file="${pump_file%%.*}.log"
pump_dir_name='DATAPUMP'
docker_image_url='a.com/database/oracle-19c:latest'
new_image_url='a.com/automation/oracle:latest'

pass_ams='password'
pass_ars='password'
pass_order='password'

# 檢查指定檔案 $base_db_file 是否存在
if [ ! -f "$base_db_file" ]; then
    echo "File $base_db_file does not exists."
    exit 0
fi

# 確認 docker 容器
id=$(docker ps -qf name="$docker_app")
# prepare oracle container
if [[ -z "$id" ]]; then
  echo "building a new docker container of oracle..."
  docker run --hostname $docker_app --name $docker_app -dit -P $docker_image_url
  sleep 50
fi

printf "預備進容器執行腳本.\r"

id=$(docker ps -qf name="$docker_app")

printf "預備進容器執行腳本..\r"

# docker container 建立緩衝
if [[ -z "$id" ]]; then
  sleep 30
fi

id=$(docker ps -qf name="$docker_app")
if [[ -z "$id" ]]; then
  echo "無法啟動，中斷"
  exit 1
fi

printf "預備進容器執行腳本...\r"
# 等待容器建立
# wait

sleep 0.5
printf "預備進容器執行腳本....\r"
printf "                           \r"

# 初始化 oracle 服務環境
docker exec -i $docker_app bash << INSTALL_DB
    printf "開始執行腳本\n"

    mkdir -p $pump_dir
    chown -R oracle:oinstall $pump_dir
    ls -la $pump_dir/

    su - oracle;

    lsnrctl reload
    echo "lsnrctl reloaded"

    sqlplus /nolog << SETUP_NEWDB

        startup;

        -- login
        conn / as sysdba;
        prompt logged.;

        CREATE OR REPLACE DIRECTORY $pump_dir_name AS '$pump_dir';
        CREATE OR REPLACE DIRECTORY DATAFILE AS '$pump_datafil';
        CREATE OR REPLACE DIRECTORY DPDIR AS '/';

        -- 清除舊帳資料
        DROP USER ELECAGENT CASCADE;
        DROP USER ELECUSER CASCADE;
        DROP USER ECECGAME_GP CASCADE;

        prompt user dropped.;

        -- pumper
        CREATE USER pumper IDENTIFIED BY "$pass_order";
        GRANT CREATE SESSION TO pumper;
        GRANT UNLIMITED TABLESPACE TO pumper;
        GRANT IMP_FULL_DATABASE TO pumper;
        GRANT DBA TO pumper;

        -- tablespace
        CREATE TABLESPACE ars DATAFILE 'ars.dbf' SIZE 5G autoextend on NEXT 500M maxsize 30G;
        CREATE TABLESPACE ams DATAFILE 'ams.dbf' SIZE 5G autoextend on NEXT 500M maxsize 30G;

        -- user
        CREATE USER ececgame IDENTIFIED BY $pass_order;
        GRANT CREATE SESSION TO ececgame;
        CREATE USER ececgame_gp IDENTIFIED BY $pass_order;
        GRANT CREATE SESSION TO ececgame_gp;
        CREATE USER center_db IDENTIFIED BY $pass_order;
        GRANT CREATE SESSION TO center_db;
        CREATE USER reporter IDENTIFIED BY $pass_order;
        GRANT CREATE SESSION TO reporter;

        prompt all user created.;
        exit;

    SETUP_NEWDB

INSTALL_DB


# 傳入檔案
docker cp $base_db_file $docker_app:$pump_dir


# 新資料庫
docker exec -i $docker_app bash << IMPORT_DB

    echo "----------- 開始建立新資料庫 -----------"

    ls -la $base_db_file
    su - oracle

    echo "備份 $base_db_file 開始匯入 ..."
    echo "impdp "pumper/$pass_order" DIRECTORY=$pump_dir_name DUMPFILE="$pump_file" LOGFILE="$log_file" SCHEMAS=\('ELECAGENT','ELECUSER'\) CLUSTER=N;"
    impdp "pumper/$pass_order" DIRECTORY=$pump_dir_name DUMPFILE="$pump_file" LOGFILE="$log_file" SCHEMAS=\('ELECAGENT','ELECUSER'\) CLUSTER=N;
    echo "轉倒結束"

    rm $base_db_file

IMPORT_DB

printf "準備打包\n"
printf "打包上傳.\r"
# docker build .
docker commit -a Avery $id $new_image_url
printf "打包上傳..\r"
docker push $new_image_url
printf "打包上傳...\r"
docker stop $id && docker rm $id
printf "打包上傳....\r"
docker rmi $new_image_url
echo "執行完成"

