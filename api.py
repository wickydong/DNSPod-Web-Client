#! /usr/bin/env python
# coding=utf-8

import json
import logging
import requests

class DNSPodAPI:
    """共通返回:
        -1 登陆失败
        -2 API 使用超出限制
        -3 不是合法代理 (仅用于代理接口)
        -4 不在代理名下 (仅用于代理接口)
        -7 无权使用此接口
        -8 登录失败次数过多,账号被暂时封禁
        -10 参数错误
        -99 此功能暂停开放,请稍候重试
        1 操作成功
        2 只允许 POST 方法
        3 未知错误
        6 用户 ID 错误 (仅用于代理接口)
        7 用户不在您名下 (仅用于代理接口)
    """
    def __init__(self, login_email, login_password):
        self.params = dict(
            login_email = login_email,
            login_password = login_password,
            format = "json",
            lang = "cn",
            error_on_empty = "no",
        )

        self.requests = requests.Session()
        self.requests.headers['User-Agent'] = "Anran ClientToy/1.0.0 (qar@outlook.com)"

    # Account related
    def UserDetail(self):
        """
        用途:     获取账户信息
        接口地址:  https://dnsapi.cn/User.Detail
        提交方法:  POST
        提交参数:  公共参数
        响应代码:  共通返回
        """
        r = self.requests.post("https://dnsapi.cn/User.Detail", data=self.params)
        return r.json()

    def UserModify(self):
        pass

    def UserpasswdModify(self):
        pass

    def UseremailModify(self):
        pass

    def TelephoneverifyCode(self):
        pass

    def UserLog(self):
        pass


    # Domain related
    def DomainCreate(self):
        pass

    def DomainList(self):
        """
        用途:     获取域名列表
        接口地址:  https://dnsapi.cn/Domain.List
        提交方法:  POST
        提交参数:  公共参数;
                  type{all,mine,share,ismark,pause,vip}(optinal); 
                  offset(optinal);
                  length(optinal);
                  group_id(optinal);
        响应代码:  共通返回;
                  6 记录开始的偏移无效
                  7 共要获取的记录的数量无效
                  9 没有任何域名

        """
        r = self.requests.post("https://dnsapi.cn/Domain.List", data=self.params)
        logging.info(r.json())
        return r.json()

    def DomainRemove(self):
        pass

    def DomainStatus(self):
        pass

    def DomainInfo(self, kwargs):
        self.params.update(kwargs)
        r = self.requests.post("https://dnsapi.cn/Domain.Info", data=self.params)
        return r.json()

    def DomainLog(self):
        pass

    def DomainSearchenginePush(self):
        pass

    def DomainUrlincn(self):
        pass

    def DomainshareCreate(self):
        pass

    def DomainshareList(self):
        pass

    def DomainshareModify(self):
        pass

    def DomainshareRemove(self):
        pass

    def DomainTransfer(self):
        pass

    def DomainLock(self):
        pass

    def DomainLockstatus(self):
        pass

    def DomainUnlock(self):
        pass

    def DomainaliasList(self):
        pass

    def DomainaliasCreate(self):
        pass

    def DomainaliasRemove(self):
        pass

    def DomaingroupList(self):
        pass

    def DomaingroupCreate(self):
        pass

    def DomaingroupModify(self):
        pass

    def DomaingroupRemove(self):
        pass

    def DomainChangegroup(self):
        pass

    def DomainIsmark(self):
        pass

    def DomainRemark(self):
        pass

    def DomainPurview(self):
        pass

    def DomainAcquire(self):
        pass

    def DomainAcquiresend(self):
        pass

    def DomainAcquirevalidate(self):
        pass

    def RecordType(self):
        pass

    def RecordLine(self):
        pass


    # Record related
    def RecordCreate(self, kwargs):
        self.params.update(kwargs)
        r = self.requests.post("https://dnsapi.cn/Record.Create", data=self.params)
        return r.json()

    def RecordList(self, domain_id):
        self.params.update({"domain_id": domain_id})
        r = self.requests.post("https://dnsapi.cn/Record.List", data=self.params)
        return r.json()
        

    def RecordModify(self, kwargs):
        self.params.update(kwargs)
        r = self.requests.post("https://dnsapi.cn/Record.Create", data=self.params)
        return r.json()

    def RecordRemove(self):
        pass

    def RecordDdns(self):
        pass

    def RecordRemark(self, domain_id, remark):
        self.params.update(dict(
            domain_id = domain_id,
            remark = remark
        ))
        r = self.requests.post("https://dnsapi.cn/Record.Remark", data=self.params)
        return r.json()

    def RecordInfo(self):
        pass

    def RecordStatus(self):
        pass

    # 宕机监控
    def MonitorListsubdomain(self):
        pass

    def MonitorListsubvalue(self):
        pass

    def MonitorList(self):
        pass

    def MonitorCreate(self):
        pass

    def MonitorModify(self):
        pass

    def MonitorRemove(self):
        pass

    def MonitorInfo(self):
        pass

    def MonitorSetstatus(self):
        pass

    def MonitorGethistory(self):
        pass

    def MonitorUserdesc(self):
        pass

    def MonitorGetdowns(self):
        pass






























































