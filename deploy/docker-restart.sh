#!/bin/bash

ENV="$1"
SCRIPT_NAME="$2"

JENKINS_USERNAME=
JENKINS_API_TOKEN=""

DOCKER_STRING="docker-"
if [[ "$SCRIPT_NAME" == *"wt"* ]]; then
  DOCKER_STRING=
  echo "包含 wt 字符串時，jenkins 的開頭不包含 docker-"
fi

echo "用 for 迴圈來重啟每一個容器"
for key in $(jq -r '.env.local | keys | .[]' env.json); do
  echo '取得最後一次成功的 build'
  number=$(curl -s -u "${JENKINS_USERNAME}:${JENKINS_API_TOKEN}" "https://ci.com/job/$DOCKER_STRING$key-$ENV/lastSuccessfulBuild/buildNumber")
  echo "serverName:$key buildNumber:$number"

  if [ "$key" = "ams-api" ]; then
    echo "就 ams 命名有時不一定要和上游一樣，所以這邊取得上游的 build number"
    key="ams-api-server"
  fi

  if [ "$key" = "wt-ams-api" ]; then
    echo "就 ams 命名有時不一定要和上游一樣，所以這邊取得上游的 build number"
    key="wt-ams-api-server"
  fi

  if [[ "$SCRIPT_NAME" == *"wt"* ]] && [[ $ENV == "stage" ]]; then
    echo "重啟 wt 的 stg 環境"
    docker restart "${key}-stg" && echo "成功重啟 $key"
  else
    if [[ "$key" == cog-* ]]; then
      echo "重啟cog"
      docker restart "${key}" && echo "成功重啟 $key"
    else
      echo "重啟"
      docker restart "${key}-${ENV}" && echo "成功重啟 $key"
    fi
  fi

done

echo "遍歷伺服器列表"
for server in $(jq -r '.env.local | to_entries[] | .value.host' env.json); do
  echo "正在檢查 $server 的連接狀況"
  start=$(date +%s) # 取得現在的 Unix 時間戳記
  while true; do
    host="${server#*//}"
    host="${host%%:*}"
    port="${server##*:}"
    port="${port%/}"

    # 使用 nc 檢查連接狀況
    if nc -z -w 3 "$host" "$port" &>/dev/null; then
      echo "成功：可以連接到 $server"
      break # 若連接成功，則跳出迴圈
    else
      echo "失敗：無法連接到 $server，正在重試..."
    fi
    now=$(date +%s)                 # 取得現在的 Unix 時間戳記
    if ((now - start >= 180)); then # 如果已經嘗試超過3分鐘，則結束
      echo "錯誤：在3分鐘內無法連接到 $server"
      break
    fi
    sleep 5 # 每次嘗試的間隔為5秒
  done
done
