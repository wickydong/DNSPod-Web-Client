#! /usr/bin/env python
# coding=utf-8

import json
import hashlib
import pymongo
import StringIO
import logging
import tornado.web

from api import DNSPodAPI

db = pymongo.Connection()['dnspod']

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = db.user.find_one({"session": self.get_cookie("session")})
        if user:
            return (user['email'], user['password'])
        else:
            return None

    @property
    def DAPI(self):
        client = self.get_current_user()
        return DNSPodAPI(client[0], client[1])


class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        member = self.get_current_user()
        resp = self.DAPI.DomainList()
        self.render("index.html", resp=resp, email=member[0])


class ExportHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        domain_ids= self.get_arguments("id", None)
        chunks = []
        for domain_id in domain_ids:
            domain_info = self.DAPI.DomainInfo({"domain_id": domain_id})
            record_list = self.DAPI.RecordList(domain_id)
            chunks.append(self.gen_backup(domain_info, record_list))
        backup_file = "\n\n".join(chunks)
        if len(domain_ids) == 1:
            backup_file_name = u"域名记录备份_%s.txt" % domain_info['domain']['name']
        else:
            backup_file_name = u"域名记录备份_共%d个域名.txt" % len(domain_ids)
        self.set_header ('Content-Type', 'text/plain')
        self.set_header ('Content-Disposition', 
                          'attachment; filename='+backup_file_name)
        self.finish(backup_file.encode("utf-8"))

    def post(self):
        chunk = self.request.files['backup'][0]['body'].strip('\n')
        for i in chunk.split("\n\n"):
            r = i.split("\n")
            for record in r[3:]:
                (name, type_, line, value, mx, ttl, remark) = record.split("\t")
                kwargs = dict(
                    domain_id = r[1],
                    sub_domain = name,
                    record_type = type_,
                    record_line = line,
                    value = value,
                    mx = mx,
                    ttl = ttl,
                )
                self.DAPI.RecordModify(kwargs)
                self.DAPI.RecordRemark(r[1], remark)
        self.redirect("/")


    def gen_backup(self, domain_info, record_list):
        BACKUP_VALUE_CN = [u"主机", u"类型", u"线路", u"记录值", u"MX优先级", u"TTL", u"备注"]
        BACKUP_VALUE_EN = [u'name', u'type', u'line', u'value', u'mx', u'ttl', u'remark']
        chunk_header = "\n".join([domain_info['domain']['name'], 
                                  domain_info['domain']['id'],
                                  "|".join(BACKUP_VALUE_CN)])
        record_item_list = []
        for r in record_list['records']:
            record_item_list.append("\t".join([r[i] for i in BACKUP_VALUE_EN]))
        chunk_records = "\n".join(record_item_list)
        return "\n".join([chunk_header, chunk_records])

    def parse_backup_file(self, chunk):
        pass


class LoginHandler(BaseHandler):
    def get(self):
        self.render("signin.html", error="")

    def post(self):
        email = self.get_argument("email", None)
        password = self.get_argument("password", None)
        api = DNSPodAPI(email, password)
        resp = api.UserDetail()
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
            self.render("signin.html", error=(resp['status']['message']))

class LogoutHandler(BaseHandler):
    def get(self):
        try:
            member = self.get_current_user()
            db.user.remove({"email": member[0]})
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