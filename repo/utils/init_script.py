import datetime
import os
import sys
import django
from repo.models import RepositoryGuideModel
from repo.init_data.tool_data import REPO_GUIDE_DICT


def init_repository_guide():
    """制品库使用指引"""
    print(" [SUCCESS] {} init_repository_guide Running".format(str(datetime.datetime.now()).rsplit(".", 1)[0]))
    for key, value in REPO_GUIDE_DICT.items():
        repo_guide = RepositoryGuideModel.fetch_one(format=key)
        if not repo_guide:
            RepositoryGuideModel.create(format=key, content=value)
        else:
            repo_guide.update(content=value)
    return 1


# if __name__ == '__main__':
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
#     import datetime
#
#     # os.environ.setdefault("BK_ENV", "production")     # 生产环境解注改行
#     # os.environ.setdefault("BK_ENV", "testing")        # 开发环境解注改行
#     sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
#     import django
#
#     django.setup()
#     from repo.models import RepositoryGuideModel
#     from repo.init_data.tool_data import REPO_GUIDE_DICT
#
#     init_repository_guide()
def run():
    init_repository_guide()
