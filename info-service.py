#!/usr/bin/env python3

from gi.repository import GLib
import dbus
import dbus.service
import dbus.mainloop.glib
import xmpp
from configparser import ConfigParser
import unittest

class GtalkInformer(dbus.service.Object):

    def __init__(self, session_bus, obj_name,
                 user_id, user_pass, to_inform):
        if session_bus:
            super(GtalkInformer, self).__init__(session_bus, obj_name)
        self.user_id = user_id
        self.user_pass = user_pass
        self.to_inform = to_inform

    @dbus.service.method("local.inform.GTalkInterface",
                         in_signature='s', out_signature='')
    def send_msg(self, msg):
#        print ("%s to %s" % (str(msg), self.to_inform))
        self.send_msg_via_xmpp(self.to_inform, msg)

    def send_msg_via_xmpp(self, user, msg):
        jid = xmpp.protocol.JID(self.user_id)
        cl = xmpp.Client(jid.getDomain(),debug=[])
        cl.connect(server=('talk.google.com', 5223))
        cl.auth(jid.getNode(), self.user_pass)
        cl.send(xmpp.protocol.Message(user, msg, typ='chat'))


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    #session_bus = dbus.SessionBus()
    session_bus = dbus.SystemBus()
    name = dbus.service.BusName("local.inform.GTalk", session_bus)

    cfg = ConfigParser()
    cfg.read("/etc/info-service.ini")
    object = GtalkInformer(session_bus, '/bob',
                           user_id = cfg.get("gtalk", "user_id"),
                           user_pass = cfg.get("gtalk", "user_pass"),
                           to_inform = cfg.get("gtalk", "to_inform")
    )

    loop = GLib.MainLoop()
    print("Running informer service.")
    loop.run()

class TestGtalkInformer(unittest.TestCase):
    def test_send_msg(self):
        cfg = ConfigParser.ConfigParser()
        cfg.read("./info-service.ini")
        obj = GtalkInformer(None, None,
                            user_id = cfg.get("gtalk", "user_id"),
                            user_pass = cfg.get("gtalk", "user_pass"),
                            to_inform = cfg.get("gtalk", "to_inform"))
        obj.send_msg("Hi from unit test")

