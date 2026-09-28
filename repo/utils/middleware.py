from django.http.response import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import json
import settings
from component.status_code import error, ErrorStatusCode

from config import BK_URL, APP_CODE
from repo.models import UserInfo
from component.esb_api import EsbApi


ENV = {"dev": "", "prod": "o", "stag": "t"}


# 用于用户在访问Web应用程序的时候，处理用户的身份验证和权限控制  验证用户身份并将用户信息保存到本地数据库中
class CreateUserMiddleware(MiddlewareMixin):
    def process_view(self, request, view, arg, kwarg):

        import platform
        # print("platform.system()", platform.system())
        if (not request.COOKIES.get("bk_token")) and (platform.system() == "Windows"):
            request.COOKIES.update(**{"bk_token": "1DyCHKBiiL-K43PKnnb9W_JVHhKdqFm4P0N04aEiAudGqKluDU0i2g6Fnne147z2"})
            # request.COOKIES.update(**{"bk_token": settings.BK_TOKEN})

        if getattr(view, 'login_exempt_v2', False):
            return None
        username = None
        if request.method == "GET":
            operator = request.GET.get("operator")
            if operator:
                username = operator
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                operator = data.get("operator")
                if operator:
                    username = operator
            except Exception:
                # 上传文件
                pass
        if not username:
            token = request.COOKIES.get("bk_token")
            # bk_user = EsbApi(token).get_user_info_from_workbench()
            bk_user = EsbApi(token).get_user_info_from_workbench_or_login()
            if not bk_user:
                login_out_url = "https%3A//" + BK_URL.split("https://")[-1] + "/" + ENV.get(getattr(settings, "run_env", "dev")) +"/{}/&is_from_logout=1".format(APP_CODE)
                return JsonResponse(error(ErrorStatusCode.INVALID_TOKEN, login_out_url))
            username = bk_user.get("username")
            bk_user.pop('id', None)

            # mongo
            user = UserInfo.fetch_one(username=username)
            if not user:
                user = UserInfo.create(**bk_user)
            else:
                user = user.update(**bk_user)
            request.COOKIES["user_id"] = user.id
        else:
            user = UserInfo.fetch_one(username=username)
            token = request.COOKIES.get("bk_token")
            if not user and token:
                # bk_user = EsbApi(token).get_user_info_from_workbench()
                bk_user = EsbApi(token).get_user_info_from_workbench_or_login()
                bk_user.pop('id', None)
                username = bk_user.get("username")
                user = UserInfo.fetch_one(username=username)
                if not user:
                    user = UserInfo.create(**bk_user)
                else:
                    user = user.update(**bk_user)
                request.COOKIES["user_id"] = user.id
            elif user:
                request.COOKIES["user_id"] = user.id
            else:
                login_out_url = "https%3A//" + BK_URL.split("https://")[-1] + "/" + ENV.get(getattr(settings, "run_env", "dev")) +"/{}/&is_from_logout=1".format(APP_CODE)
                return JsonResponse(error(ErrorStatusCode.NOT_HAVE_USER_INFO, login_out_url))
        return None


"""
    这段代码是一个 Django 中间件，其作用是在用户访问 Web 应用程序时进行身份验证和权限控制，并将用户信息保存到本地数据库中。
    
        具体实现逻辑如下：
        
        1、首先，该中间件继承了 Django 的 MiddlewareMixin 类，以便使用 Django 中间件的功能。
        
        2、在 process_view 方法中，根据请求的方法（GET 或 POST）获取用户的操作者信息（operator）。
        
        3、如果没有获取到操作者信息，则从请求的 COOKIES 中获取 bk_token，然后调用 EsbApi 类的 get_user_info_from_workbench_or_login 方法，通过 bk_token 获取用户信息 bk_user。
        
        4、如果没有获取到用户信息 bk_user，则返回一个包含错误状态码和登出 URL 的 JsonResponse。
        
        5、如果获取到了用户信息 bk_user，则从 bk_user 中提取出用户名 username，并根据用户名从本地数据库中查找对应的用户记录。
        
        6、如果在本地数据库中找不到对应的用户记录，则创建一个新的用户记录，并将用户信息存储到本地数据库。
        
        7、如果在本地数据库中找到了对应的用户记录，则更新用户信息。
        
        8、最后，将用户的 ID 存储到请求的 COOKIES 中，以便后续使用。
    
    总的来说，该中间件用于验证用户身份并将用户信息保存到本地数据库中，确保用户在访问 Web 应用程序时具有有效的身份和权限。
"""