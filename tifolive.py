#!/usr/bin/env python3
import json
import random
import socket
from time import time

import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from sqlalchemy.orm import scoped_session, sessionmaker

import Settings
import models

from image import somefunction


def random_color():
    table = []
    for r in range(12):
        row = []
        for p in range(260):
            row.append('#' + ''.join([random.choice('0123456789ABCDEF') for x in range(6)]))
        table.append(row)

    return table


def encode_response(header, body):
    return {'header': header, 'body': body}


class Application(tornado.web.Application):
    tornado.options.parse_command_line()

    def __init__(self):
        handlers = [
            (r"/",
             IndexHandler),
            (r"/test",
             TestHandler),
            (r"/tifos",
             TifosHandler),
            (r"/stadiums",
             StadiumsHandler),
            (r"/contact",
             ContactHandler),
            (r"/ws/(?P<stadium>[^\/?]+)",
             WebSocketHandler),
            (r"/ajax/(?P<label>[^\/?]+)",
             AjaxHandler),
            (r"/(?P<stadium>[^\/?]+)/tifo/admin",
             TifoAdminHandler),
            (r"/(?P<stadium>[^\/?]+)/tifo/?(?P<seat>[^\/?]+)?",
             TifoLiveHandler),
            (r"/(?P<stadium>[^\/?]+)",
             StadiumHandler)
        ]
        settings = {
            "template_path": Settings.TEMPLATE_PATH,
            "static_path": Settings.STATIC_PATH,
            "debug": Settings.DEBUG,
            "cookie_secret": Settings.COOKIE_SECRET,
            "xsrf_cookies": Settings.XSRF_COOKIES
        }

        self.db = scoped_session(sessionmaker(bind=models.engine))
        # self.r = redis.StrictRedis()

        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class IndexHandler(BaseHandler):
    def get(self) -> object:
        models.create_all()
        self.render("index.html")


class TifosHandler(BaseHandler):
    def get(self):
        self.write("tifos page")


class StadiumsHandler(BaseHandler):
    def get(self):
        self.write("stadiums page")


class ContactHandler(BaseHandler):
    def get(self):
        self.write("contact page")


class TifoAdminHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.render("admin.html")


class TifoLiveHandler(BaseHandler):
    def get(self, *args, **kwargs):
        stadium = kwargs.get('stadium')
        seat = kwargs.get('seat')

        if stadium and seat:
            self.render('pixel.html', seat=seat)
        else:
            self.render('tifo.html')


class StadiumHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.write(kwargs.get('stadium', "your stadium") + "'s page")


class AjaxHandler(BaseHandler):
    def get(self, *args, **kwargs):
        if kwargs['label'] == 'tifodata':
            stadium_short = self.get_query_arguments('stadium_short')
            seat_short = self.get_query_arguments('seat_short')

            with open('static/json/output1.json') as f:
                data = json.loads(f.read())

            self.write(json.dumps({'status': 200, 'data': data}))


class TestHandler(BaseHandler):
    def get(self):
        self.render("test.html", table=somefunction())


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    users = set()

    @classmethod
    def send_users_update(cls, stadium):
        i = 0
        stadium_users = set()
        for user in cls.users:
            if user.stadium == stadium:
                stadium_users.add(user)
        for user in stadium_users:
            try:
                user.write_message(encode_response('users-online', len(stadium_users)))
            except:
                print("Error sending message in send_users_update")

    @classmethod
    def send_start_time(cls, stadium, start_time):
        for user in cls.users:
            if user.stadium == stadium:
                try:
                    user.write_message(encode_response('start-time', start_time))
                except:
                    print("Error sending message in send_start_time")

    def open(self, *args, **kwargs):
        if 'stadium' not in kwargs:
            print("Weird ...")
            return

        self.stadium = kwargs['stadium']

        WebSocketHandler.users.add(self)
        WebSocketHandler.send_users_update(self.stadium)

    def on_close(self, *args, **kwargs):
        WebSocketHandler.users.remove(self)
        WebSocketHandler.send_users_update(self.stadium)

    def on_message(self, message):
        data = json.loads(message)
        header = data['header']
        # body = data['body']

        if header == 'start':
            current_time = int(time() * 1000)
            WebSocketHandler.send_start_time(self.stadium, current_time)
            print("REQUEST : " + header)

        if header == 'start-10':
            scheduled_time = int(time() * 1000) + 10000
            WebSocketHandler.send_start_time(self.stadium, scheduled_time)
            print("REQUEST : " + header)

        elif header == 'ping-time':
            self.write_message(encode_response('pong-time', int(time() * 1000)))
            print("REQUEST : " + header)

        elif header == 'ping':
            self.write_message(encode_response('pong', ''))

        else:
            print(data)


if __name__ == "__main__":
    server = Application()
    server.listen(Settings.PORT)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** TifoLive Server Started at %s:%d ***' % (myIP, Settings.PORT))
    tornado.ioloop.IOLoop.current().start()
