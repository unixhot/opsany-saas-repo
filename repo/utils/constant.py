# 工具连接状态正常
TOOL_LINK_STATUS_SUCCESS = "正常"
# 工具连接状态异常
TOOL_LINK_STATUS_ERROR = "异常"
# 工具类型 , ('SonarQube', '代码质量')
TOOL_TYPE_LIST = [('jenkins', '持续交付'), ('git', '代码仓库'), ('repository', '制品库')]

# 制品库类型
REPOSITORY_TYPE_LIST = [("raw", "raw"), ("maven2", "maven2"), ("docker", "docker"), ("pypi", "pypi"), ("helm", "helm")]
REPOSITORY_FORMAT = ("raw", "pypi", "maven2", "docker")
