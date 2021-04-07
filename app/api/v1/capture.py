#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件        :capture.py
@说明        :
@时间        :2021/03/29 15:09:03
@作者        :Leo
@版本        :1.0
"""

from app.libs.redprint import Redprint
from app.libs.code import Sucess, Fail
from app.models.user import User
from flask import request
from app.models.capture import get_pro_list, get_conf_list, get_category_list
from app.libs.capture import _add, _erase
from app.models.module import Module
import time

now_time = int(time.time())
api = Redprint("capture")


@api.route("/user_list", methods=["GET"])
def user_list():
    """
    用户列表
    """
    user_list = User.get_login_user_list()
    return Sucess(data=user_list)


@api.route("/pro_list", methods=["GET"])
def pro_list():
    """
    项目列表
    """
    pro_list_info = get_pro_list()
    return Sucess(data=pro_list_info)


@api.route("/<int:pro_id>/conf_list", methods=["GET"])
def conf_list(pro_id):
    """
    配置列表
    """
    pro_list_info = get_conf_list(pro_id)
    return Sucess(data=pro_list_info)


@api.route("/<int:pro_id>/cate_list", methods=["GET"])
def category_list(pro_id):
    """
    分类列表
    """
    category_list_info = get_category_list(pro_id)
    return Sucess(data=category_list_info)


@api.route("/upload", methods=["POST"])
def upload_api():
    """
    同步接口
    """
    res = request.get_json()
    for api in res["data"].keys():
        for k, v in res["data"][api].items():
            _method = v["method"]
            is_api = _erase.is_api(v["headers"])
            if is_api:
                api_id = _add.add_api(k, k, _method, res["pro_id"], res["cate_id"])
                _headers = _erase._header(v["headers"])
                _dheaders = _erase._header(v["headers"], desc="desc")
                _params = _erase._params(v["url"])
                _dparams = _erase._params(v["url"], desc="desc")
                if _method == "POST":
                    if "body" in v:
                        if isinstance(v["body"], list):
                            api_module_detail = _erase._api_json(
                                k,
                                k,
                                _method,
                                _headers,
                                _dheaders,
                                _params,
                                _dparams,
                                v["body"],
                            )
                        else:
                            api_module_detail = _erase._form_data(
                                k,
                                k,
                                _method,
                                _headers,
                                _dheaders,
                                _params,
                                _dparams,
                                v["body"],
                            )
                    else:
                        api_module_detail = _erase._api_json(
                            k, k, _method, _headers, _dheaders, _params, _dparams, ""
                        )
                else:
                    api_module_detail = _erase._api_get_json(
                        k, k, _method, _headers, _dheaders, _params, _dparams
                    )
                Module.add_api_module(
                    "capture_" + str(now_time),
                    str(api_module_detail),
                    api_id,
                    res["user_id"],
                )
            else:
                Fail(msg=str(k) + "解析失败")
    return Sucess()
