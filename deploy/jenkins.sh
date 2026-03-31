# Config

echo "準備執行 jenkins.sh"
pwd

echo " build machine 目前為 jenkins 這台機器, 主要用來部署目標測試機"
echo " ####### step1 準備參數設置 ####### "
echo "$REPO 專案名稱"
REPOSITORY=$REPO

echo "$BUILD_NUMBER 是Jenkins 預設提供的環境變數。它代表了當前建置的編號，是一個連續遞增的整數"
MINOR_VERSION=$BUILD_NUMBER

echo "執行計畫名稱"
PLAN_NAME=${PLAN_NAME}

echo "取得腳本的名字"
FULL_SCRIPT_NAME="automation-${SCRIPT_NAME}-data"

echo "DB 所在IP，主要還原快照用"
DB_VM_IP=${DB_VM_IP}
DB_IP=${DB_IP}

echo "取得腳本的branch"
SCRIPT_BRANCH=${SCRIPT_BRANCH}

echo "build machine 路徑"
BUILD_MACHINE_DIR=/web/buildmachine/${REPOSITORY}-${FULL_SCRIPT_NAME}/${ENV}

echo "建立 build machine 目錄"
mkdir -p "$BUILD_MACHINE_DIR"

echo "測試目標機資訊以及動作"
echo "定義了測試目標機器的信息，例如用戶名，IP 地址，文件傳輸命令等"
TARGET_AUTOMATION_MACHINE_USER=root
TARGET_AUTOMATION_MACHINE_IP=${TEST_TARGET_MACHINE}
TARGET_AUTOMATION_MACHINE_DIR=/web/${REPOSITORY}
TARGET_AUTOMATION_MACHINE_COPY_PATH="${TARGET_AUTOMATION_MACHINE_USER}@${TARGET_AUTOMATION_MACHINE_IP}:"
TARGET_AUTOMATION_MACHINE_CMD="ssh ${TARGET_AUTOMATION_MACHINE_USER}@${TARGET_AUTOMATION_MACHINE_IP}"
ENV_PATH="/web/server-env/$REPOSITORY/env.json"

# 還原DB快照
snapshot() {
  echo "準備 DB 還原快照至 test , test 為快照名 **********************************************************************"
  if ! ssh -x root@"$DB_VM_IP" "cd /root/vmguest-mgmt;ansible-playbook -i hosts vm-revert-snapshot.yml"; then
    echo "還原快照失敗。 ！！！"
    exit 1
  fi

  # 計數器
  counter=0

  # 迴圈，直到連接開放或達到最大嘗試次數
  while [ $counter -lt 3 ]; do
    # 檢查連接
    if echo >/dev/tcp/$DB_IP/1521; then
      echo "DB端口已開放"
      break
    else
      echo "DB端口未開放，等待..."
      sleep 5
      counter=$((counter + 1))
    fi
  done

  if [ $counter -eq 3 ]; then
    echo "逾時：6分鐘後DB端口仍未開放。"
  fi
}

# git clone 測試資料
gitPullAutomationData() {
  echo "準備執行 gitPullAutomationData git clone 測試資料 **********************************************************************"
  REPO_URL="git@git.com:poc/${FULL_SCRIPT_NAME}.git"

  echo "移除 git 倉庫目錄"
  rm -rf "$FULL_SCRIPT_NAME"

  echo "進行 clone 操作..."

  git clone -b "${SCRIPT_BRANCH}" --single-branch "$REPO_URL"

  echo "刪除測試腳本，再建立測試腳本目錄"
  rm -rf "$BUILD_MACHINE_DIR"/data && echo 'Success'
  mkdir -p "$BUILD_MACHINE_DIR"/data

  echo "用來辦識測試目標機的資訊"
  mkdir -p "$BUILD_MACHINE_DIR"/data/"$MINOR_VERSION"
  echo "復製腳本資料"
  cp -r "$FULL_SCRIPT_NAME"/data/* "$BUILD_MACHINE_DIR"/data
}

# 復製 各項腳本 至目標機
runScp() {
  echo "準備執行 runScp 復製 各項腳本 至目標機 **********************************************************************"
  echo "step 將 deploy/ 目錄下的所有檔案複製到 build machine 的目錄下。"
  cp -r ./deploy/* "$BUILD_MACHINE_DIR"

  echo "建立測試目標機目錄"
  echo "在目標機器上創建了目錄，並使用 scp 命令將構建機器的文件夾中的文件複製到目標機器的目錄中。最後，代碼在目標機器上運行了 start.sh 腳本"
  ${TARGET_AUTOMATION_MACHINE_CMD} "
        rm -rf ${TARGET_AUTOMATION_MACHINE_DIR}/data && echo 'Success'
        mkdir -p ${TARGET_AUTOMATION_MACHINE_DIR}
      "

  echo "複製 .sh 檔案至測試目標機"
  scp -r "$BUILD_MACHINE_DIR"/* "$TARGET_AUTOMATION_MACHINE_COPY_PATH""$TARGET_AUTOMATION_MACHINE_DIR" && echo 'Success'
}

# 測試目標機
postAutomation() {
  echo "準備執行 postAutomation 測試目標機資訊以及動作 **********************************************************************"

  JENKINS_USERNAME=
  JENKINS_API_TOKEN=""
  MINOR_VERSION=$(curl -s -u "${JENKINS_USERNAME}:${JENKINS_API_TOKEN}" "https://ci.com/job/$REPOSITORY-docker-$ENV/lastSuccessfulBuild/buildNumber")

  echo "執行 docker-restart.sh 重啟api服務容器 & 取得最後一次成功的 build number & 檢查連接"
  echo "執行 restart.sh automation docker run"
  ${TARGET_AUTOMATION_MACHINE_CMD} "
      cd ${TARGET_AUTOMATION_MACHINE_DIR} &&
      cp ${ENV_PATH} env.json &&
      bash -x ./docker-restart.sh ${ENV} $SCRIPT_NAME &&
      bash -x ./restart.sh ${REPOSITORY} ${ENV} ${MINOR_VERSION} ${PLAN_NAME} &&
      find /var/log/automation -type d -ctime +7 -exec rm -r {} \;
    "
}

totalTimeStart=$(date +%s)
snapshot
gitPullAutomationData
runScp
postAutomation
totalTimeEnd=$(date +%s)
duration=$((totalTimeEnd - totalTimeStart))
echo "step Jenkins 總耗費時間 $duration  seconds"
