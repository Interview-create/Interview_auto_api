#!/bin/bash

echo "執行 build/docker-build.sh"

# 說明：將其打包並上傳到 harbor
# 執行指令：bash -x docker-build.sh
# 程式有更新 還是得去 https://ci.com/job/automation-docker/ 出 build

echo "在本地執行時"
echo "export BUILD_NUMBER=106"
echo "cd automation 移到根目錄"
echo "bash -x docker-build.sh"

# shellcheck disable=SC2016
REGISTRY_USER='robot$harbor-backend'

WEB='-web'
if [ "$REPO" = "automation" ]; then
  echo "REPO 是 automation"
  WEB=''
else
  echo "REPO 是 automation-web"
fi

REPOSITORY=automation
BUILD_VERSION=$BUILD_NUMBER

# 組出對應環境的hobar url
REGISTRY_ENV=$ENV
REGISTRY_USER='robot$harbor-backend'

if [ $ENV = "dev" ]; then
    REGISTRY_ENV=dev
elif [ $ENV = "stg" ] || [ $ENV = "stage" ]; then
    REGISTRY_ENV=stg
elif [ $ENV = "rel" ]; then
    REGISTRY_ENV=stg
fi

HOBOR_URL=$REGISTRY_ENV-reg.com

echo "登入docker harbor"
docker login ${HOBOR_URL} -u ${REGISTRY_USER} --password-stdin < build/docker-token-${REGISTRY_ENV}
# cat build/docker-token-${REGISTRY_ENV} | docker login ${REGISTRY_ENV}-reg.com -u ${REGISTRY_USER} --password-stdin

ls -l build

echo "build docker image"
docker build -t ${REPOSITORY} --build-arg WEB="$WEB" -f build/Dockerfile .

echo "上傳需 tag docker image"
docker tag ${REPOSITORY} ${HOBOR_URL}/${REPOSITORY}/"${REPOSITORY}""${WEB}":"$BUILD_VERSION"

echo "上傳 docker image"
docker push ${HOBOR_URL}/${REPOSITORY}/"${REPOSITORY}""${WEB}":"$BUILD_VERSION"


### 由於防火牆 policy 調整，各個環境各自拆開不得互相存取。因此，AUTOMATION 的 HARBOR 上傳改成一式兩份，同時上傳 DEV 與 STAGE 環境
### @TODO: 後續可以與 QA 討論，看是否用 Jenkins 選單，讓 RD/QA 選擇要出哪一個環境的 AUTOMATION
REGISTRY_ENV=stg

echo "登入docker harbor"
docker login ${HOBOR_URL} -u ${REGISTRY_USER} --password-stdin < build/docker-token-${REGISTRY_ENV}
# cat build/docker-token-${REGISTRY_ENV} | docker login ${REGISTRY_ENV}-reg.com -u ${REGISTRY_USER} --password-stdin

ls -l build

echo "build docker image"
docker build -t ${REPOSITORY} --build-arg WEB="$WEB" -f build/Dockerfile .

echo "上傳需 tag docker image"
docker tag ${REPOSITORY} ${HOBOR_URL}/${REPOSITORY}/"${REPOSITORY}""${WEB}":"$BUILD_VERSION"

echo "上傳 docker image"
docker push ${HOBOR_URL}/${REPOSITORY}/"${REPOSITORY}""${WEB}":"$BUILD_VERSION"
