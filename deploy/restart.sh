#!/bin/bash
# 檔案以 /bin/bash 啟動
# 定義了專案名稱的變數 REPO，設定 registry 的使用者名稱 REGISTRY_USER

# shellcheck disable=SC2016
REGISTRY_USER='robot$harbor-backend'

echo "step 準備執行 start-${REPO}.sh"
totalTimeStart=$(date +%s)

REPO=$1
echo "第一個參數為 REPO ${REPO}"

ENV=$2
echo "第二個參數為 ENV $ENV"

MINOR_VERSION=$3
echo "第三個參數為 MINOR_VERSION $MINOR_VERSION"

PLAN_NAME=$4
echo "第四個參數為 PLAN_NAME $PLAN_NAME"

REGISTRY_ENV=dev

if [ "${ENV}" = "stage" ]
then
    REGISTRY_ENV=stg
fi

echo "step 檢查是否有名稱為 ${REPO} 的 docker container 存在，如果存在則停止並刪除它"
docker ps -a | grep "${REPO}" && docker stop --time=30 "${REPO}" && docker rm -f "${REPO}"

echo "step 登入 harbor"
echo " 登入 $REGISTRY_ENV-reg.com registry，使用在檔案 'docker-token-$REGISTRY_ENV' 中的密碼，登入使用者為 REGISTRY_USE"
docker login $REGISTRY_ENV-reg.com -u ${REGISTRY_USER} --password-stdin < docker-token-$REGISTRY_ENV

echo "step 執行 ${REPO}, 這裡會自行判斷版本差異，不同會 pull 下來，反之。"
docker run \
  --name "$REPO" \
  -d \
  -e ARGS="$PLAN_NAME" \
  -v /var/log/"$REPO":/app/log/ \
  -v /web/"$REPO"/data:/app/data \
  -v /root/dcpt/c-shared-so:/root/dcpt/c-shared-so \
  --env "envConfig=$(<./env.json)" \
  $REGISTRY_ENV-reg.com/"$REPO"/"$REPO":"$MINOR_VERSION"

echo "step 刪除 images"
nohup docker images $REGISTRY_ENV-reg.com/"$REPO"/"$REPO" --format '{{.Repository}}:{{.Tag}}' --quiet | tail -n +2 | xargs -r docker rmi -f &


totalTimeEnd=$(date +%s)
duration=$((totalTimeEnd - totalTimeStart))
echo "step restart ${REPO} 總耗費時間: ${duration} seconds"
