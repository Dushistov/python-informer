#!/usr/bin/env python2

import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import xmpp
import ConfigParser

class GtalkInformer(dbus.service.Object):

    def __init__(self, session_bus, obj_name,
                 user_id, user_pass, to_inform):
        super(GtalkInformer, self).__init__(session_bus, obj_name)
        self.user_id = user_id
        self.user_pass = user_pass
        self.to_inform = to_inform
    
    @dbus.service.method("local.inform.GTalkInterface",
                         in_signature='s', out_signature='')
    def send_msg(self, msg):
        print (str(msg))
        self.send_msg_via_xmpp(self.to_inform, msg)

    def send_msg_via_xmpp(self, user, msg):
        jid = xmpp.protocol.JID(self.user_id)
        cl = xmpp.Client(jid.getDomain(),debug=[])
        cl.connect()
        cl.auth(jid.getNode(), self.user_pass)
        cl.send(xmpp.protocol.Message(user, msg, typ='chat'))
    

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    #session_bus = dbus.SessionBus()
    session_bus = dbus.SystemBus()
    name = dbus.service.BusName("local.inform.GTalk", session_bus)

    cfg = ConfigParser.ConfigParser()
    cfg.read("/etc/info-service.ini")    
    object = GtalkInformer(session_bus, '/bob',
                           user_id = cfg.get("gtalk", "user_id"),
                           user_pass = cfg.get("gtalk", "user_pass"),
                           to_inform = cfg.get("gtalk", "to_inform")
    )

    mainloop = gobject.MainLoop()
    print "Running informer service."
    mainloop.run()
