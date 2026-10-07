# LivingTV 公开频道配置

此仓库只发布频道配置，不包含应用源码、APK、签名密钥、观看历史或诊断日志。TV源码仓库保持私有。

- `config/uhd-channels.json`：5个4K试播条目，版本2026100703。河北当前线路声音异常待修复，不能视为声音稳定通过。
- `config/channels.json`：正式审核频道目录，当前为空，不伪造来源审核。
- `config/trial-channels.m3u`：原49频道列表，文件保持。通用导入会替换上次导入列表，请勿用来追加4K。

公开仓库上传后，可直接使用Raw HTTPS地址，无需先开通Pages：
`https://raw.githubusercontent.com/574516151-netizen/TV-config/main/config/uhd-channels.json`

地址需经实际GET与JSON校验成功后才接入APK默认设置。GitHub域名可达性取决于网络，应用更新失败使用有效缓存/内附目录，不中断已加载频道。不要在配置中存放账号、DRM密钥、凭据请求头或时效签名URL。

修改内容必须提高`version`。重复同版本只允许完全相同的配置。更新前真实解码/声音/当地网络仍须验证；目录本身不是播放器验收证明。

若需要Pages，可在Settings→Pages选择GitHub Actions，然后手动运行Publish public channel configuration；工作流只发布白名单静态配置文件。免费账号需公开仓库，源码仓库不用改公开。
