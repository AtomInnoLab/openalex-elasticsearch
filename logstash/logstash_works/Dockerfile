# logstash_works/Dockerfile
FROM docker.elastic.co/logstash/logstash:7.17.2

# 安装 JDBC 输出插件
RUN logstash-plugin install logstash-output-jdbc

# 删除默认 pipeline
RUN rm -f /usr/share/logstash/pipeline/logstash.conf

# 拷贝 pipeline 到镜像内部
COPY pipeline/ /usr/share/logstash/pipeline/

# 拷贝 sql_last_value 文件
COPY sql_last_value.yml /usr/share/logstash/sql_last_value.yml

# 拷贝 jars
COPY jars/ /usr/share/jars/

# 修改目录属主，让 logstash 用户可写
USER root
RUN chown -R logstash:logstash /usr/share/logstash

# 切回 logstash 用户
USER logstash

# 设置工作目录
WORKDIR /usr/share/logstash

