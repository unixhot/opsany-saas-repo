## 生产环境启动

```
INSTALL_PATH="/opt/opsany"
PAAS_DOCKER_REG="registry.cn-beijing.aliyuncs.com/opsany"
mkdir -p ${INSTALL_PATH}/logs/rbac

docker run -d --restart=always --name opsany-saas-ce-rbac \
       -p 7001:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-supervisor.ini:/etc/supervisord.d/rbac.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-uwsgi.ini:/opt/opsany/uwsgi/rbac.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-init.py:/opt/opsany/rbac/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py:/opt/opsany/rbac/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/rbac:/opt/opsany/logs/rbac \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-rbac:1.7.0
```
