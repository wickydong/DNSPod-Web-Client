#! /usr/bin/env python
# coding=utf-8

import json
import hashlib
import pymongo
import logging
import tornado.web
import requests

db = pymongo.Connection()['dnspod']

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.data = dict(
            format = "json",
            lang = "cn",
            error_on_empty = "no",
        )
        self.requests = requests.Session()
        self.requests.headers['User-Agent'] = "Anran ClientToy/1.0.0 (qar@outlook.com)"

    def get_current_user(self):
        user = db.user.find_one({"session": self.get_cookie("session")})
        if user:
            return {"login_email": user['email'], "login_password": user['password']}
        else:
            return None

    ## DNSPod API
    def UserDetail(self, auth):
        self.data.update(auth)
        r = self.requests.post("https://dnsapi.cn/User.Detail", data=self.data)
        return r.json()

    def DomainInfo(self, kwargs):
        self.data.update(self.get_current_user())
        self.data.update(kwargs)
        r = self.requests.post("https://dnsapi.cn/Domain.Info", data=self.data)
        return r.json()

    def DomainList(self):
        self.data.update(self.get_current_user())
        r = self.requests.post("https://dnsapi.cn/Domain.List", data=self.data)
        return r.json()

    def RecordList(self, kwargs):
        self.data.update(self.get_current_user())
        self.data.update(kwargs)
        r = self.requests.post("https://dnsapi.cn/Record.List", data=self.data)
        return r.json()

    def RecordRemove(self, kwargs):
        self.data.update(self.get_current_user())
        self.data.update(kwargs)
        r = self.requests.post("https://dnsapi.cn/Record.Remove", data=self.data)
        return r.json()    

    def RecordCreate(self, kwargs):
        self.data.update(self.get_current_user())
        self.data.update(kwargs)
        r = self.requests.post("https://dnsapi.cn/Record.Create", data=self.data)
        return r.json()



class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        member = self.get_current_user()
        resp = self.DomainList()
        self.render("index.html", resp=resp, email=member['login_email'])


class ExportHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        domain_ids= self.get_arguments("id", None)
        chunks = []
        for domain_id in domain_ids:
            domain_info = self.DomainInfo({"domain_id": domain_id})
            record_list = self.RecordList({"domain_id": domain_id})
            chunks.append(self.gen_backup(domain_info, record_list))

        if len(domain_ids) == 1:
            backup_file_name = u"域名记录备份_%s.json" % domain_info['domain']['name']
        else:
            backup_file_name = u"域名记录备份_共%d个域名.json" % len(domain_ids)

        self.set_header ('Content-Type', 'text/json')
        self.set_header ('Content-Disposition', 
                          'attachment; filename='+backup_file_name)
        self.finish(json.dumps(chunks, sort_keys=True, indent=4))

    def post(self):
        chunk = json.loads(self.request.files['backup'][0]['body'].strip('\n'))
        # First: Delete current records
        for domain in chunk:
            record_list = self.RecordList({"domain_id": domain['id']})
            for r in record_list['records']:
                self.RecordRemove(dict(
                    domain_id = domain['id'],
                    record_id = r['id'],
                ))
        # Second: Create records
        for domain in chunk:
            for record in domain['records']:
                self.RecordCreate(dict(
                    domain_id = domain['id'],
                    sub_domain = record['name'],
                    record_type = record['type'],
                    record_line = record['line'],
                    value = record['value'],
                    mx = record['mx'],
                    ttl = record['ttl'],
                ))
        self.finish()

    def gen_backup(self, domain_info, record_list):
        records = []
        for r in record_list['records']:
            records.append(dict(
                #id = r['id'],
                name = r['name'],
                type = r['type'],
                line = r['line'],
                value = r['value'],
                mx = r['mx'],
                ttl = r['ttl'],
                remark = r['remark'],
                enabled = r['enabled'],
            ))
        
        return dict(
            name = domain_info['domain']['name'],
            id = domain_info['domain']['id'],
            records = records,
        )


class LoginHandler(BaseHandler):
    def get(self):
        self.render("signin.html", error="")

    def post(self):
        email = self.get_argument("email", None)
        password = self.get_argument("password", None)
        resp = self.UserDetail({"login_email": email, "login_password":password})
        print resp
        if resp['status']['code'] == "1":
            session = hashlib.sha256(email+password).hexdigest()
            if not db.user.find_one({"email":email, "password":password}):
                db.user.insert(dict(
                    email = email,
                    password = password,
                    session = session
                ))
            self.set_cookie(name="session", 
                            value=session)
            self.redirect("/")
        else:
            self.render("signin.html", error=resp['status']['message'])


class LogoutHandler(BaseHandler):
    def get(self):
        try:
            member = self.get_current_user()
            db.user.remove({"email": member['login_email']})
            self.clear_all_cookies()
            self.redirect("/login")
        except:
            pass

handlers = [
    (r"/", IndexHandler),
    (r"/export", ExportHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
]