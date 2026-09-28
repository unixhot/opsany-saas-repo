from component.esb_api import EsbApi
from repo.models import UserInfo


class GetUserInfo:
    def get_user_info(self, request=None, bk_token=None):
        if request:
            username = request.COOKIES.get("bk_token_username")
        else:
            esb_obj = EsbApi(bk_token)
            user_info = esb_obj.get_user_info()
            username = user_info.get("username")
        return UserInfo.fetch_one(username=username)

    def get_user_role(self, request=None, bk_token=None):
        if not bk_token:
            bk_token = request.COOKIES.get("bk_token")
        esb_obj = EsbApi(bk_token)
        user_info = esb_obj.get_user_info()
        return user_info.get("role")