FROM mysql/mysql-server:5.7

ENV MYSQL_ROOT_PASSWORD=root \
    MYSQL_ROOT_HOST=localhost

ADD seedDB.sql /docker-entrypoint-initdb.d

EXPOSE 3306
