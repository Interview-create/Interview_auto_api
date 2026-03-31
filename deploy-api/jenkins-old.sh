# 說明：
# 確認是否有輸入必要的參數 $ENV 和 $REPO，如果沒有則輸出錯誤信息並退出；
# 確認是否開啟了自動化測試功能，如果沒有則直接退出；
# 獲取上游的 Jenkins build number；
# 定義測試目標機器的信息，包括用戶名，IP 地址，文件傳輸命令等；
# 執行 postAutomation() 函數，該函數主要執行以下操作：
#   創建測試目標機目錄；
#   使用 scp 命令將構建機器的文件夾中的文件複製到目標機器的目錄中；
#   在目標機器上運行 start.sh 腳本。
# 最後，計算整個腳本的總耗時，並輸出。

echo "準備執行 automation 的 deploy-api/jenkins.sh"
pwd
ls

echo " build machine 目前為 jenkins 這台機器, 主要用來部署目標測試機 "
echo " ####### step1 準備參數設置 ####### "
REPOSITORY=$REPO
REPOSITORY_URL=$REPOSITORY
MINOR_VERSION=
DOCKER_STRING="docker-"

# 處理 server name 跟 images 不一樣的情況
processParameters() {
  if [ "$REPOSITORY" = "ams-api-server" ]; then
    echo "就 ams 命名有時不一定要和上游一樣，所以這邊取得上游的 build number"
    REPOSITORY_URL="ams-api"
    echo $REPOSITORY_URL
  fi

  if [ "$REPOSITORY" = "wt-ams-api-server" ]; then
    echo "就 ams 命名有時不一定要和上游一樣，所以這邊取得上游的 build number"
    REPOSITORY_URL="wt-ams-api"
    echo $REPOSITORY_URL
  fi

  if [[ "$REPOSITORY" == *"wt"* ]]; then
    DOCKER_STRING=
    echo "包含 wt 字符串"
  fi
}
processParameters

# 處理版本 號 特殊情況
processVersion() {
  echo "取得上游的 build number"
  JENKINS_USERNAME=
  JENKINS_API_TOKEN=""

  if [ "$BUILD_NUMBER" == "lastSuccessfulBuild" ]; then
    MINOR_VERSION=$(curl -s -u "${JENKINS_USERNAME}:${JENKINS_API_TOKEN}" "https://ci.com/job/$DOCKER_STRING$REPOSITORY_URL-$ENV/lastSuccessfulBuild/buildNumber")
  else
    MINOR_VERSION=$BUILD_NUMBER
  fi

  if [ "$REPOSITORY" = "cog-api" ]; then
    echo "就 cog 命名有時不一定要和上游一樣，所以這邊取得上游的 build number"
    MAJOR_VERSION=1.0
    MINOR_VERSION=$MAJOR_VERSION.$MINOR_VERSION
    echo $REPOSITORY_URL
  fi
}
processVersion

# build machine 位址
# step2 在上游 Upstream Projects 時已經cp過了。
BUILD_MACHINE_DIR=/web/buildmachine/${REPOSITORY}/${ENV}

# 測試目標機資訊以及動作
# 定義了測試目標機器的信息，例如用戶名，IP 地址，文件傳輸命令等。
TARGET_AUTOMATION_MACHINE_USER=root
TARGET_AUTOMATION_MACHINE_IP=${TEST_TARGET_MACHINE}
TARGET_AUTOMATION_MACHINE_DIR=/web/${REPOSITORY}
TARGET_AUTOMATION_MACHINE_COPY_PATH="${TARGET_AUTOMATION_MACHINE_USER}@${TARGET_AUTOMATION_MACHINE_IP}:"
TARGET_AUTOMATION_MACHINE_CMD="ssh ${TARGET_AUTOMATION_MACHINE_USER}@${TARGET_AUTOMATION_MACHINE_IP}"

postAutomation() {
  echo "準備執行 postAutomation 測試目標機資訊以及動作"

  echo "建立測試目標機目錄"
  echo "在目標機器上創建了目錄，並使用 scp 命令將構建機器的文件夾中的文件複製到目標機器的目錄中。最後，代碼在目標機器上運行了 start.sh 腳本"
  ${TARGET_AUTOMATION_MACHINE_CMD} "
        mkdir -p ${TARGET_AUTOMATION_MACHINE_DIR}
        mkdir -p /web/server-env/${REPOSITORY}
      "

  ls "$BUILD_MACHINE_DIR"

  echo "複製 .sh 檔案至測試目標機"
  scp -r "$BUILD_MACHINE_DIR"/* "$TARGET_AUTOMATION_MACHINE_COPY_PATH""$TARGET_AUTOMATION_MACHINE_DIR"
  scp -r deploy-api/api-env/"$ENV"/"$REPOSITORY"/* "$TARGET_AUTOMATION_MACHINE_COPY_PATH"/web/server-env/"$REPOSITORY"/

  echo "執行 docker run"
  ${TARGET_AUTOMATION_MACHINE_CMD} "
      cd ${TARGET_AUTOMATION_MACHINE_DIR} &&
      cp -r /web/server-env/${REPOSITORY}/* . &&
      bash -x ./restart.sh ${REPOSITORY} ${ENV} ${MINOR_VERSION}
    "
}

totalTimeStart=$(date +%s)
postAutomation
totalTimeEnd=$(date +%s)
duration=$((totalTimeEnd - totalTimeStart))
echo "step Jenkins 總耗費時間" $duration " seconds"
