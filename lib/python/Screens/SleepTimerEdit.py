from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Input import Input
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.config import config
from SleepTimer import SleepTimerEntry
import time

class SleepTimerEdit(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["red"] = Pixmap()
		self["green"] = Pixmap()
		self["yellow"] = Pixmap()
		self["blue"] = Pixmap()
		self["red_text"] = Label()
		self["green_text"] = Label()
		self["yellow_text"] = Label()
		self["blue_text"] = Label()
		self.updateColors()
		
		self["pretext"] = Label(_("Shutdown Dreambox after"))
		self["input"] = Input(text = str(self.session.nav.SleepTimer.getCurrentSleepTime()), maxSize = False, type = Input.NUMBER)
		self["aftertext"] = Label(_("minutes"))
		
		self["actions"] = NumberActionMap(["SleepTimerEditorActions"], 
		{
			"exit": self.close,
			"select": self.select,
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
			"selectLeft": self.selectLeft,
			"selectRight": self.selectRight,
			"disableTimer": self.disableTimer,
			"toggleAction": self.toggleAction,
			"toggleAsk": self.toggleAsk
		}, -1)
		
	def updateColors(self):
		if self.session.nav.SleepTimer.isActive():
			self["red_text"].setText(_("Timer status:") + " " + _("Enabled"))
		else:
			self["red_text"].setText(_("Timer status:") + " " + _("Disabled"))
		if config.SleepTimer.action.value == "shutdown":
			self["green_text"].setText(_("Sleep timer action:") + " " + _("Deep Standby"))
		elif config.SleepTimer.action.value == "standby":
			self["green_text"].setText(_("Sleep timer action:") + " " + _("Standby"))

		if config.SleepTimer.ask.value:
			self["yellow_text"].setText(_("Ask before shutdown:") + " " + _("yes"))
		else:
			self["yellow_text"].setText(_("Ask before shutdown:") + " " + _("no"))
		self["blue_text"].setText(_("Settings"))
		
		
	def select(self):
		self.session.nav.SleepTimer.setSleepTime(int(self["input"].getText()))
		self.session.openWithCallback(self.close, MessageBox, _("The sleep timer has been acitvated."), MessageBox.TYPE_INFO)
	
	def keyNumberGlobal(self, number):
		self["input"].number(number)
		
	def selectLeft(self):
		self["input"].left()

	def selectRight(self):
		self["input"].right()
	
	def disableTimer(self):
		if self.session.nav.SleepTimer.isActive():
			self.session.nav.SleepTimer.clear()
		else:
			self.session.nav.SleepTimer.setSleepTime(int(self["input"].getText()))
		self.updateColors()
		
	def toggleAction(self):
		if config.SleepTimer.action.value == "shutdown":
			config.SleepTimer.action.value = "standby"
		elif config.SleepTimer.action.value == "standby":
			config.SleepTimer.action.value = "shutdown"
		self.updateColors()
		
	def toggleAsk(self):
		config.SleepTimer.ask.value = not config.SleepTimer.ask.value
		self.updateColors()