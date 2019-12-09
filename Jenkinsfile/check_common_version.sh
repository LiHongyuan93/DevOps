#! /bin/bash
# The scritps aim to check if common version exist or not in .m2 library and build "backend-mate-common-service-dev" job when common version not exist.
# Essential parameters:
#   文件路径

SERVICE=(${1//// })
SERVICE=${SERVICE[1]}
BRANCH=$2

# Check common version exist or not
function check_common_version(){
    num=0
    cd $SERVICE
    echo "service name:$SERVICE"
    echo "branch:$BRANCH"
    git checkout $BRANCH
    git status
    version_line=`sed -n '/<artifactId>mate-common-service/{n;p}' pom.xml`		                # find common version in pom.xml
    common_version_list=(`ls ~/.m2/repository/com/gymbomate/common/mate-common-service`)		# loop local common repository to get all common version
    echo "common_version_list: $common_version_list"

    for common_version in ${common_version_list[@]}											     # compare common version with common repo
    do
        if [[ "$version_line" =~ "$common_version" ]];then
        echo "这个版本号$common_version在common中存在，所以不用编译common service"
        num=1
        break
        fi
    done
    return $num
}

# build "backend-mate-common-service-dev" job to create newest common service version
function compiled_package() {
#    /usr/bin/java -jar /root/jenkins-cli.jar -auth iris:c704a1f555c4d77923f2b317bfd032eb -s http://172.16.13.101:8080/ build backend-mate-common-service-dev &
    /usr/bin/java -jar /root/jenkins-cli.jar -auth iris:c704a1f555c4d77923f2b317bfd032eb -s http://172.16.13.101:8080/ build test &
    sleep 90
}


check_common_version $SERVICE $BRANCH
echo "-----------------------------------------------------------"
echo $?
if [[ $? == '0']];then
    echo "检测到没有最新的common 版本，现在打包最新一次提交的common，正在自动构建 'backend-mate-common-service-dev'"
    compiled_package
    check_common_version
    if [[ $? == '0']];then
        echo "common打包完毕，发现还是没有pom.xml所需的common版本，请先检查您的common版本号写的是否正确！"
        exit 1
    elif [[ $? == '0']];then
        echo "common 打包完毕，可以匹配pom.xml所需common版本"
    else
        echo "common 打包失败，请查看'backend-mate-common-service-dev'报错信息"
        exit 1
    fi
fi