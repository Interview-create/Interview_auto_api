# Config

echo "準備執行 jenkins.sh"
pwd

# build machine 目前為 jenkins 這台機器, 主要用來部署目標測試機
# ####### step1 準備參數設置 #######
REPOSITORY=$REPO

# $BUILD_NUMBER 是Jenkins 預設提供的環境變數。它代表了當前建置的編號，是一個連續遞增的整數。
MINOR_VERSION=$BUILD_NUMBER

PLAN_NAME=${PLAN_NAME}

# 取得上游的 build number
JENKINS_USERNAME=
JENKINS_API_TOKEN=""

# build machine 位址
# 如果 BUILD_MACHINE_IP 是指向 127.0.0.1，代表使用 Jenkins 上的機器當成 build machine(e.g. build-slave-2)
# CP 指的是命令 "cp"，在 Unix-like 系統中是用來複製檔案或目錄的指令。
BUILD_MACHINE_DIR=/web/buildmachine/${REPOSITORY}/${ENV}

# step2 建立 build machine 目錄, 以其 report 目錄
mkdir -p "$BUILD_MACHINE_DIR"
mkdir -p /data/build_machine/docker/builder/workspace/"$JOB_NAME"/report

# 測試目標機資訊以及動作
# 定義了測試目標機器的信息，例如用戶名，IP 地址，文件傳輸命令等。
TARGET_AUTOMATION_MACHINE_USER=root
TARGET_AUTOMATION_MACHINE_IP=${TEST_TARGET_MACHINE}
TARGET_AUTOMATION_MACHINE_DIR=/web/${REPOSITORY}
TARGET_AUTOMATION_MACHINE_COPY_PATH="${TARGET_AUTOMATION_MACHINE_USER}@${TARGET_AUTOMATION_MACHINE_IP}:"
TARGET_AUTOMATION_MACHINE_CMD="ssh ${TARGET_AUTOMATION_MACHINE_USER}@${TARGET_AUTOMATION_MACHINE_IP}"

postAutomation() {
  echo "準備執行 postAutomation 測試目標機資訊以及動作"

  # step 複製環境的 env.json  dev.json -> env.json
  # cp ./src/"${ENV}".json ./deploy/env.json

  # step 將 deploy/ 目錄下的所有檔案複製到 build machine 的目錄下。
  cp -r ./deploy-web/* "$BUILD_MACHINE_DIR"

  # 建立測試目標機目錄
  # 在目標機器上創建了目錄，並使用 scp 命令將構建機器的文件夾中的文件複製到目標機器的目錄中。最後，代碼在目標機器上運行了 start.sh 腳本
  ${TARGET_AUTOMATION_MACHINE_CMD} "
        mkdir -p ${TARGET_AUTOMATION_MACHINE_DIR}
      "

  # 複製 .sh 檔案至測試目標機
  scp -r "$BUILD_MACHINE_DIR"/* "$TARGET_AUTOMATION_MACHINE_COPY_PATH""$TARGET_AUTOMATION_MACHINE_DIR"

  MINOR_VERSION=$(curl -s -u "${JENKINS_USERNAME}:${JENKINS_API_TOKEN}" "https://ci.com/job/$REPOSITORY-docker-$ENV/lastSuccessfulBuild/buildNumber")

  # 執行 docker run
  ${TARGET_AUTOMATION_MACHINE_CMD} "
      cd ${TARGET_AUTOMATION_MACHINE_DIR} &&
      cp /web/server-env/${REPOSITORY}/env.json env.json &&
      bash -x ./restart.sh ${REPOSITORY} ${ENV} ${MINOR_VERSION} ${PLAN_NAME}
    "
}

totalTimeStart=$(date +%s)
postAutomation
totalTimeEnd=$(date +%s)
duration=$((totalTimeEnd - totalTimeStart))
echo "step Jenkins 總耗費時間" $duration " seconds"
