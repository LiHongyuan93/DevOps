本项目用于存放jenkins pipeline脚本。脚本可以实现CI(持续开发)、CD（持续部署），实现自动化运维

前提条件：

**Jenkins** 
1. 已经下载好插件：
    Maven Repository Server Plugin ，并在jenkins slave node上下载好maven
    Rancher，并在jenkins中配置好和rancher 的集成

2. Jenkins 的账号有权限执行jenkins job，并且在配置好个人账号的API tocken用于代码中调度
3. 已经存在Jenkins job：xxx-$branch （用于编译common service）
4. 已经存在Jenkins job：xxx_$branch (用于升级rancher 微服务)

**gitlab**

配置好ssh key，有权限拉取git项目代码

**阿里云**

docker login验证登录好，保证本地可以推送docker镜像到xx云镜像仓库