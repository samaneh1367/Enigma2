from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Tools import Notifications

from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

from enigma import eTimer

my_global_session = None

from Components.config import config, ConfigSubsection, configElement, configSequence, getConfigListEntry, configsequencearg, configElementBoolean
from Components.ConfigList import ConfigList

config.FritzCall = ConfigSubsection()
config.FritzCall.hostname = configElement("config.FritzCall.hostname", configSequence, [192,168,178,254], configsequencearg.get("IP"))
config.FritzCall.enable = configElementBoolean("config.FritzCall.enable", 0)

class FritzCallSetup(Screen):
	skin = """
		<screen position="100,100" size="550,400" title="FritzCall Setup" >
		<widget name="config" position="20,10" size="460,350" scrollbarMode="showOnDemand" />
		</screen>"""


	def __init__(self, session, args = None):
		from Tools.BoundFunction import boundFunction
		
		print "screen init"
		Screen.__init__(self, session)
		self.onClose.append(self.abort)
		
		# nun erzeugen wir eine liste von elementen fuer die menu liste.
		self.list = [ ]
		self.list.append(getConfigListEntry(_("Call monitoring"), config.FritzCall.enable))
		self.list.append(getConfigListEntry(_("Fritz!Box FON IP address"), config.FritzCall.hostname))
		self["config"] = ConfigList(self.list)

		# DO NOT ASK.		
		self["setupActions"] = NumberActionMap(["SetupActions"],
		{
			"left": boundFunction(self["config"].handleKey, config.key["prevElement"]),
			"right": boundFunction(self["config"].handleKey, config.key["nextElement"]),
			"1": self.keyNumberGlobal,
			"2": self.keyNumberGlobal,
			"3": self.keyNumberGlobal,
			"4": self.keyNumberGlobal,
			"5": self.keyNumberGlobal,
			"6": self.keyNumberGlobal,
			"7": self.keyNumberGlobal,
			"8": self.keyNumberGlobal,
			"9": self.keyNumberGlobal,
			"0": self.keyNumberGlobal,
			"save": self.save,
			"cancel": self.cancel,
			"ok": self.save,
		}, -1)
	# FIX ME.
	def keyNumberGlobal(self, number):
		if self["config"].getCurrent()[1].parent.enabled == True:
			self["config"].handleKey(config.key[str(number)])

	def abort(self):
		print "aborting"

	def save(self):
		for x in self["config"].list:
			x[1].save()
		if fritz_call is not None:
			fritz_call.connect()
		self.close()

	def cancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()

class FritzProtocol(LineReceiver):
	delimiter = "\r\n"
	
	def lineReceived(self, line):

#15.07.06 00:38:54;CALL;1;4;<provider>;<callee>;
#15.07.06 00:38:58;DISCONNECT;1;0;
#15.07.06 00:39:22;RING;0;<caller>;<outgoing msn>;
#15.07.06 00:39:27;DISCONNECT;0;0;

		a = line.split(';')
		(date, event) = a[0:2]
		
		if event == "RING":
			phone = a[4]
			number = a[3]
			text = _("incoming call!\n%s calls on %s!") % (number, phone)
			timeout = 10
		else:	
			return
		
		Notifications.AddNotification(MessageBox, text, type=MessageBox.TYPE_INFO, timeout=timeout)

class FritzClientFactory(ReconnectingClientFactory):

	initialDelay = 20
	maxDelay = 500
	
	def __init__(self):
		self.hangup_ok = False

	def startedConnecting(self, connector):
		Notifications.AddNotification(MessageBox, _("Connecting to Fritz!Box..."), type=MessageBox.TYPE_INFO, timeout=2)
	
	def buildProtocol(self, addr):
		Notifications.AddNotification(MessageBox, _("Connected to Fritz!Box!"), type=MessageBox.TYPE_INFO, timeout=2)
		self.resetDelay()
		return FritzProtocol()
	
	def clientConnectionLost(self, connector, reason):
		if not self.hangup_ok:
			Notifications.AddNotification(MessageBox, _("Disconnected from\nFritz!Box! (%s)\nretrying...") % reason.getErrorMessage(), type=MessageBox.TYPE_INFO, timeout=4)
		ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
	
	def clientConnectionFailed(self, connector, reason):
		Notifications.AddNotification(MessageBox, _("Connection to Fritz!Box\nfailed! (%s)\nretrying...") % reason.getErrorMessage(), type=MessageBox.TYPE_INFO, timeout=4)
		ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

class FritzCall:
	def __init__(self):
		self.dialog = None
		self.d = None
		self.connect()
		
	def connect(self):	
		self.abort()
		if config.FritzCall.enable.value:
			f = FritzClientFactory()
			self.d = (f, reactor.connectTCP("%d.%d.%d.%d" % tuple(config.FritzCall.hostname.value), 1012, f))

	def shutdown(self):
		self.abort()

	def abort(self):
		if self.d is not None:
			self.d[0].hangup_ok = True 
			self.d[0].stopTrying()
			self.d[1].disconnect()
			self.d = None

def main(session):
	session.open(FritzCallSetup)

fritz_call = None

def autostart(reason, **kwargs):
	global fritz_call
	
	# ouch, this is a hack	
	if kwargs.has_key("session"):
		global my_global_session
		my_global_session = kwargs["session"]
		return
	
	print "autostart"
	if reason == 0:
		fritz_call = FritzCall()
	elif reason == 1:
		fritz_call.shutdown()
		fritz_call = None

def Plugins(**kwargs):
 	return [ PluginDescriptor(name="FritzCall", description="Display Fritzbox-Fon calls on screen", where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main),
 		PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart) ]