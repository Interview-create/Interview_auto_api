# Use an official Python 3 runtime as the base image
# 使用官方的 Python 3 運行時作為基礎鏡像
FROM python:3.9-slim-buster

# 定義參數 ARG
ARG WEB

# 將參數設置為環境變數
ENV MY_WEB=$WEB

# Installing Oracle instant client
WORKDIR    /opt/oracle
RUN        apt-get update && apt-get install -y libaio1 wget unzip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip \
            && unzip instantclient-basiclite-linuxx64.zip \
            && rm -f instantclient-basiclite-linuxx64.zip \
            && cd /opt/oracle/instantclient* \
            && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci \
            && echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf \
            && ldconfig

# Set the working directory to /app
# 將工作目錄設置為/app
WORKDIR /app

RUN mkdir -p /app/log

# Copy the current directory contents into the container at /app
# 將當前目錄的內容複製到容器中的/app
COPY ./src/ /app

# Install any necessary packages
# 安裝必要的軟件包
RUN pip3 install --no-cache-dir -r requirements.txt

# Define environment variable
# 定義環境變量
ENV NAME World

# 暴露端口，確保它與您的 Flask 應用程序使用的端口一致
EXPOSE 5001

# 做判斷並執行相應的操作
CMD if [ "$MY_WEB" = "-web" ]; then \
      gunicorn -preload -w 4 -b 0.0.0.0:5001 app:app; \
    else \
      python -u main.py; \
    fi