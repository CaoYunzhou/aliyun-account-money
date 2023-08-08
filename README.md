### 阿里云账号余额通知到钉钉群

- 每天定时统计阿里云账户余额以及上个月的余额发送到钉钉通知群


###### 环境变量说明

| 环境变量名称        | 必填   | 备注                                       |
| ----------------- | ------ | --------------------------|
| `WEBHOOK_URL`     | 必填    | 钉钉群的webhook机器人地址
| `SECRET`          | 必填    |  安全设置的加签秘钥        |
| `AK`              | 必填    |  阿里云的AK秘钥        |
| `SK`              | 必填    |  阿里云的SK秘钥  |

##### Kubernetes

- 更改kubernetes/k8s_crontab.yaml的变量

- 执行cronjobs脚本
    ```
    kubectl apply -f kubernetes/k8s_crontab.yaml
    ```
