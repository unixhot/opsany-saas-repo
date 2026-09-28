from collections import OrderedDict

import yaml


class GetUserInfo:
    def get_user_info(self, request=None, bk_token=None):
        from component.esb_api import EsbApi
        if not bk_token:
            bk_token = request.COOKIES.get("bk_token")
        esb_obj = EsbApi(bk_token)
        user_info = esb_obj.get_user_info()
        from repo.models import UserInfo
        return UserInfo.fetch_one(username=user_info.get("username"))

    def get_user_role(self, request=None, bk_token=None):
        from component.esb_api import EsbApi
        if not bk_token:
            bk_token = request.COOKIES.get("bk_token")
        esb_obj = EsbApi(bk_token)
        user_info = esb_obj.get_user_info()
        return user_info.get("role")


def first_error_message(form):
    error_data = form.errors.as_data()
    error_data_list = list(error_data.items())
    # if not error_data_list:
    #     return ""
    error_message = error_data_list[0][1][0].message
    message = "{}".format(error_message)
    return message


# 生成有序的字典（传参为yaml字符串）
def ordered_yaml_load(yaml_str, Loader=yaml.SafeLoader,
                      object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(yaml_str, OrderedLoader)


# 生成有序的yaml字符串（传参为OrderedDict）
def ordered_yaml_dump(data, stream=None, Dumper=yaml.SafeDumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


class QuickSort:
    def __init__(self, reverse=False, order_fields="created_at"):  # reverse: 是否倒序 默认正序
        self.reverse = reverse
        self.order_fields = order_fields

    # 快速排序，将标签按照commit顺序排序
    def partition(self, arr, low, high):
        i = (low - 1)  # 最小元素索引
        pivot = arr[high].get(self.order_fields)

        for j in range(low, high):

            # 当前元素小于或等于 pivot
            if self.reverse:
                if arr[j].get(self.order_fields) >= pivot:
                    i = i + 1
                    arr[i], arr[j] = arr[j], arr[i]
            else:
                if arr[j].get(self.order_fields) <= pivot:
                    i = i + 1
                    arr[i], arr[j] = arr[j], arr[i]

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return (i + 1)

    def quick_sort(self, arr, low, high):
        if low < high:
            pi = self.partition(arr, low, high)

            self.quick_sort(arr, low, pi - 1)
            self.quick_sort(arr, pi + 1, high)

    def run(self, arr):
        """
        快速排序
        :param arr: 排序数组，元素可以是字符串数字字典等
        :return:
        """
        n = len(arr)
        self.quick_sort(arr, 0, n - 1)
        return arr


if __name__ == '__main__':
    li = [
        {'name': '胡兴起3', 'created_at': '2023-03-11 13:27:08', 'data_type': 'folder', 'id': 42, },
        {'name': '胡兴起4', 'created_at': '2023-03-08 14:10:44', 'data_type': 'folder', 'id': 17, },
        {'name': '胡兴起1', 'created_at': '2023-03-11 13:05:17', 'data_type': 'article', 'unique_code': 'qws', },
        {'name': '胡兴起2', 'created_at': '2023-03-07 13:40:00', 'data_type': 'article', 'unique_code': 'ffv', }
    ]
    print("old:", li)
    QuickSort(reverse=True, order_fields="created_at").run(li)
    print("new:", li)
