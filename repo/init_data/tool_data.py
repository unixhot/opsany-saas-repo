REPO_GUIDE_DICT = {
    "maven2": """- #### 设置凭证

  ##### 手动配置

  编辑您的 **settings.xml**。

  请将下方 `[PASSWORD]` 替换成您的密码。请妥善保管好您的配置，不要随意分享给他人。

  ```
  <!-- 一般情况 maven 的通用 settings.xml 在 .m2 文件夹下, 项目内 settings.xml 也可以进行设置，优先级更高 -->
  <settings>
      <!-- omitted xml -->
      <servers>
          <server>
              <id>{id}</id>
              <username>[USERNAME]</username>
              <password>[PASSWORD]</password>
          </server>
      </servers>
  </settings>
  ```

  #### 推送

  1. 初始化您的 **pom.xml**。

     ```
     <project>
         <!-- 必要属性 -->
         <groupId>[GROUP_ID]</groupId>
         <artifactId>[ARTIFACT_ID]</artifactId>
         <version>[VERSION]</version>

         <!-- omitted xml -->
         <distributionManagement>
             <repository>
                 <!--必须与 settings.xml 的 id 一致-->
                 <id>{id}</id>
                 <name>maven2</name>
                 <url>{url}</url>
             </repository>
         </distributionManagement>
     </project>
     ```

  2. 推送您的 Maven 包。

     ```
     mvn deploy
     ```

  #### 拉取

  1. 编辑您的 **settings.xml** 文件。

     ```
     <settings>
         <!-- omitted xml -->
         <profiles>
             <profile>
                 <id>Repository Proxy</id>
                 <activation>
                     <activeByDefault>true</activeByDefault>
                 </activation>
                 <repositories>
                     <repository>
                         <id>{id}</id>
                         <name>maven2</name>
                         <url>{url}</url>
                         <releases>
                             <enabled>true</enabled>
                         </releases>
                         <snapshots>
                             <enabled>true</enabled>
                         </snapshots>
                     </repository>
                 </repositories>
             </profile>
         </profiles>
     </settings>
     ```

  2. 编辑您的 **pom.xml** 文件。

     ```
     <project>
         <dependencies>
             <dependency>
                 <groupId>[GROUP_ID]</groupId>
                 <artifactId>[ARTIFACT_ID]</artifactId>
                 <version>[VERSION]</version>
             </dependency>
         </dependencies>
     </project>
     ```

  3. 执行拉取命令。

     ```
     mvn install
     ```

  #### 相关文档

  [maven.apache.org](https://maven.apache.org/)""",
    "raw": """#### 推送

##### 使用 curl 推送

```
curl -T <FILE.EXT> -u [USERNAME] "{url}/<PACKAGE>?version=<VERSION>"
```

- `<VERSION>` 为**非必填**项，默认为 **latest**。
- 支持 直接上传 或拖拽到当前页面进行上传。

#### 拉取

```
curl --fail -L -u [USERNAME] "{url}/<PACKAGE>?version=<VERSION>" -o <FILE.EXT>
```

- `<VERSION>` 为**非必填**项，默认为 **latest**。

#### 删除

```
curl -X DELETE -u [USERNAME] "{url}/<PACKAGE>?version=<VERSION>"
```

- `<VERSION>` 为**非必填**项，默认为 **latest**。""",
    "docker": """#### 设置凭证

##### 手动配置

```
docker login -u [USERNAME] {url}
```

#### 推送

1. 给本地的镜像打标签。

   ```
   docker tag <LOCAL_IMAGE_TAG> {url}/<PACKAGE>
   ```

2. 推送您的 docker 镜像。

   ```
   docker push {url}/<PACKAGE>
   ```

#### 拉取

```
docker pull  {url}/<PACKAGE>
```

#### 相关文档

[docs.docker.com](https://docs.docker.com/)""",
    "pypi": """#### 设置凭证

##### 手动配置

在您的 **$HOME/.pypirc** 文件添加以下配置。

请将下方 `<PASSWORD>` 替换成您的密码。请妥善保管好您的配置，不要随意分享给他人。

```
[distutils]
index-servers =pypi
[pypi]
repository: {url}
username: [USERNAME]
password: <PASSWORD>
```

##### MacOS / Linux

在您的 **$HOME/.pip/pip.conf** 文件添加以下配置。

```
[global]
index-url = {url}:<PASSWORD>{url}/simple
```

##### Windows

在您的 **%HOME%/pip/pip.ini** 文件添加以下配置。

```
[global]
index-url =  {url}:<PASSWORD>{url}/simple
```

#### 推送

```
twine upload -r pypi dist/*
```

#### 拉取

```
pip install <PACKAGE>
```

#### 相关文档

[pypi.org](https://pypi.org/)
""",
    "nuget": """#### 设置凭证

##### 自动生成配置

推荐使用访问令牌生成命令。

##### 手动配置

请将下方 `<PASSWORD>`替换成您的密码。

```
nuget sources Add -Username "<USERNAME>" -Password "<PASSWORD>" -Name "nuget" -Source "{url}/v3/index.json"
```

#### 推送

```
nuget push -ApiKey api -Source "nuget" my_package.nupkg
```

#### 拉取

```
nuget install -Source "nuget" <PACKAGE>
```

#### 删除

```
nuget delete -ApiKey api -Source "nuget" <PACKAGE> <VERSION>
```

**注意：通过本操作删除的包将无法恢复。**

#### 相关文档

[nuget.org](https://www.nuget.org/)""",
    "helm": """#### 设置凭证

##### 手动配置

在您的 **~/.helm/config.yaml** 文件中添加以下配置，确保替换 `[USERNAME]` 和 `[PASSWORD]`。

```
repositories:
  - name: my-helm-repo
    url: {url}
    username: [USERNAME]
    password: [PASSWORD]
```

#### 推送

1. 初始化您的 Helm 包。确保您的 Helm Chart 结构正确。

2. 使用 Helm 打包命令将 Helm Chart 打包成 `.tgz` 文件。

```
helm package <chart-directory>
```

3. 推送您的 Helm Chart。

```
helm push <chart-file>.tgz {url}
```

#### 拉取

1. 添加 Helm 仓库。

```
helm repo add my-helm-repo {url}
```

2. 更新本地的 Helm 仓库信息。

```
helm repo update
```

3. 安装您的 Helm Chart。

```
helm install <release-name> my-helm-repo/<chart-name>
```

#### 相关文档

[helm.sh/docs](https://helm.sh/docs/)
"""
}
