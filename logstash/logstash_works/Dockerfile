FROM docker.elastic.co/logstash/logstash:7.17.2

# 安装 JDBC 插件
RUN logstash-plugin install logstash-output-jdbc

# 如果需要特定版本可以这样
# RUN logstash-plugin install --version 5.0.7 logstash-output-jdbc
