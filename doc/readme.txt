一、前言

Domain-HTTP-header-query-system 是一个强大的全网探测检查工具，特别适用于CDN厂商或者有使用到CDN厂商的业务域名。

对比传统的全网检查工具，它的特点有：
1、操作简单，可以任意指定代理域名或CNAME，直接在网页上就可以完成全网检查工作
2、功能强大，可以检测 httpcode，content-length，etag，last-modified，https crt expire time等相关信息
3、不需要维护一套节点ip列表。它会通过edns，进行全网解析去获取平台所有节点列表

二、安装

1、前端建议部署nginx充当代理网关
2、定义访问域名，然后将 index.html 放置根目录（里面的跳转域名也需要记得修改）
3、将python程序和dig程序上传至对应目录，并执行即可

注意：
因为其依赖ipip.net的ip库（需要进行ip归属地解析，你也可以不用到它），假如需要的话，您最好去ipip.net下载一个ip库文件（本人无权限共享该ip库）

三、其它

开发者联系：hnxiezan@163.com
