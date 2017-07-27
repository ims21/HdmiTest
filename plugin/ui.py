# for localized messages  	 
from . import _
#################################################################################
#
#    HdmiTest plugin for OpenPLi-Enigma2
#    version:
VERSION = "0.41"
#    by ims (c)2012-2017
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#################################################################################

from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.config import *
from Components.ActionMap import ActionMap
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from enigma import eTimer, getDesktop
from enigma import eHdmiCEC
import struct
import os

HD = False
if getDesktop(0).size().width() >= 1280:
	HD = True

config.plugins.HdmiTest = ConfigSubsection()
config.plugins.HdmiTest.cmd = ConfigSelection(default = "0x82", choices = [
	("0x04", "0x04 - Image View On"),
	("0x0D", "0x0d - Text View On"),
	("0x36", "0x36 - Standby"),
	("0x46", "0x46 - Give OSD Name"),
	("0x47", "0x47 - Set OSD Name"),
	("0x70", "0x70 - System Mode Audio Request"),
	("0x71", "0x71 - Give Audio Status"),
	("0x720","0x72 - Set System Audio Mode - Off"),
	("0x721","0x72 - Set System Audio Mode - On"),
	("0x7a0","0x7a - Report Audio Status - Mute Off"),
	("0x7a1","0x7a - Report Audio Status - Mute On"),
	("0x7d", "0x7d - Give System Audio Mode Status"),
	("0x7e0","0x7e - System Audio Mode Status - Off"),
	("0x7e1","0x7e - System Audio Mode Status - On"),
	("0x81", "0x81 - Routing information"),
	("0x82", "0x82 - Active Source"),
	("0x83", "0x83 - Give Physical Address"),
	("0x84", "0x84 - Report physical address"),
	("0x85", "0x85 - Request Active Source"),
	("0x86", "0x86 - Set stream path"),
	("0x8c", "0x8c - Give Device Vendor ID"),
	("0x8d2","0x8d - Menu Request - Query"),
	("0x8d0","0x8d - Menu Request - Activate"),
	("0x8d1","0x8d - Menu Request - Deactivate"),
	("0x8e0","0x8e - Menu Status - Activated"),
	("0x8e1","0x8e - Menu Status - Deactivated"),
	("0x8f", "0x8f - Give Device Power Status"),
	("0x91", "0x91 - Get menu language"),
	("0x9d", "0x9d - Inactive Source"),
	("0x9f", "0x9f - Get CEC version"),
	])

config.plugins.HdmiTest.realphysicaladdress = ConfigYesNo(default = True)
config.plugins.HdmiTest.broadcast = ConfigSelection(default = "0x00", choices=[
		("0x00",_("TV (0x00)")),
		("0x0f",_("Broadcast (0x0f)")),
		("0x05",_("Audio system (0x05)")),
		("0x01",_("Recording device 1 (0x01)")),
		("0x02",_("Recording device 2 (0x02)")),
		("0x03",_("STB1 (0x03)")),
		("0x04",_("DVD1 (0x04)")),
		("0x06",_("STB2 (0x06)")),
		("0x07",_("STB3 (0x07)")),
		("0x08",_("DVD2 (0x08)")),
		("0x09",_("Recording device 3 (0x09))")),
		("0x0a",_("Reserved (0x0a))")),
		("0x0b",_("Reserved (0x0b))")),
		("0x0c",_("Reserved (0x0c))")),
		("0x0d",_("Reserved (0x0d))")),
		("0x0e",_("Free (0x0e))"))
	])
config.plugins.HdmiTest.hh = ConfigSelectionNumber(min = 0, max = 0xf, stepwidth = 1, default = 0, wraparound = True)
config.plugins.HdmiTest.hl = ConfigSelectionNumber(min = 0, max = 0xf, stepwidth = 1, default = 0, wraparound = True)
config.plugins.HdmiTest.lh = ConfigSelectionNumber(min = 0, max = 0xf, stepwidth = 1, default = 0, wraparound = True)
config.plugins.HdmiTest.ll = ConfigSelectionNumber(min = 0, max = 0xf, stepwidth = 1, default = 0, wraparound = True)
config.plugins.HdmiTest.testmode = ConfigYesNo(default = False)
config.plugins.HdmiTest.special = ConfigSelection(default="0",choices=[
	("0",_("None")),
	("1",_("Disable numeric hotkeys")),
	("2",_("Disable all hotkeys")),
	("3",_("Disable HDMI-CEC plugin")),
	("4",_("Disable HDMI-CEC plugin and Num")),
	("5",_("Disable all"))
	])
cfg = config.plugins.HdmiTest

# CEC Version's table:
CecVersion = ["1.1","1.2","1.2a","1.3","1.3a","1.4","2.0?","unknown"]
# Operation codes:
opCode = {
	0x00:"<Polling Message>",
	0x04:"<Image View On>",
	0x0d:"<Text View On>",
	0x32:"<Set Menu Language>",
	0x36:"<Standby>",
	0x46:"<Give OSD Name>",
	0x47:"<Set OSD Name>",
	0x70:"<System Mode Audio Request>",
	0x71:"<Give Audio Status>",
	0x72:"<Set System Audio Mode>",
	0x7a:"<Report Audio Status>",
	0x7d:"<Give System Audio Mode Status>",
	0x7e:"<System Audio Mode Status>",
	0x80:"<Routing Change>",
	0x81:"<Routing Information>",
	0x82:"<Active Source>",
	0x83:"<Give Physical Address>",
	0x84:"<Report Physical Address>",
	0x85:"<Request Active Source>",
	0x86:"<Set Stream Path>",
	0x87:"<Device Vendor ID>",
	0x89:"<Vendor Command>", 
	0x8c:"<Give Device Vendor ID>",
	0x8d:"<Menu Request>",
	0x8e:"<Menu Status>",
	0x8f:"<Give Device Power Status>",
	0x90:"<Report Power Status>",
	0x91:"<Give Device Power Status>",
	0x9e:"<CEC Version>",
	0x9d:"<Inactive Source>",
	0x9e:"<CEC Version>",
	0x9f:"<Get CEC Version>",
	}
# returned abort codes:
abortReason = {
	0x00:"Unrecognized opcode",
	0x01:"Not in correct mode to respond",
	0x02:"Cannot provide source",
	0x03:"Invalid operand",
	0x04:"Refused",
	0x05:"Unable to determine",
	}
# power status return codes:
powerStatus = {
	0x00:"(On)",
	0x01:"(Standby)",
	0x02:"(In transition Standby to On)",
	0x03:"(In transition On to Standby)",
	}
# opcode for broadcast only:
BROADCAST = [0x32, 0x72, 0x80, 0x81, 0x82, 0x84, 0x85, 0x86, 0x87, 0x8a, 0x8b, 0xA0]
# opcode for direct address or broadcast:
BOTH = [0x36, 0x72, 0x8a, 0x8b, 0xA0]

BB  = [0x70, 0x81, 0x82, 0x86, 0x9d]
BBB = [0x84]
TXT = [0x32, 0x47]

class HdmiTest(Screen, ConfigListScreen):
	skin = """
	<screen name="HdmiTest" position="center,center" size="640,400" title="HdmiTest" >
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />

		<widget name="key_red"    position="0,0"   size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_green"  position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue"   position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

		<ePixmap pixmap="skin_default/buttons/key_menu.png" alphatest="on" position="568,10" size="35,25" />

		<widget name="config" position="10,40" size="620,210" zPosition="1" itemHeight="30" font="Regular;25" scrollbarMode="showOnDemand"/>
		<widget name="address" position="10,262" size="310,25" zPosition="1" font="Regular;20" foregroundColor="blue"/>
		<widget name="sendto" position="320,262" size="310,25" zPosition="1" font="Regular;20" foregroundColor="blue"/>

		<ePixmap pixmap="skin_default/div-h.png" position="0,285" zPosition="2" size="640,2" />

		<widget name="ltx" position="10,290" size="40,20" zPosition="1" font="Regular;18" halign="left" foregroundColor="green"/>
		<widget name="txtext" position="50,290" size="220,105" zPosition="1" font="Regular;18" halign="left"/>
		<widget name="lrx" position="270,290" size="40,20" zPosition="1" font="Regular;18" halign="left" foregroundColor="red"/>
		<widget name="rxtext" position="310,290" size="320,105" zPosition="1" font="Regular;18" halign="left"/>
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setup_title = _("HdmiTest")

		self.HDMICEC = None
		for routine in eHdmiCEC.getInstance().messageReceived.get():
			if str(routine).find("Components.HdmiCec.HdmiCec"):
				index = eHdmiCEC.getInstance().messageReceived.get().index(routine)
				self.HDMICEC = eHdmiCEC.getInstance().messageReceived.get().pop(index)
				self.activateHdmiCec()
		
		self['address'] = Label()
		self['sendto'] = Label()
		self.mainMenu()
		self.onChangedEntry = []
		ConfigListScreen.__init__(self, self.HdmiTestMenuList, session = session, on_change = self.changedEntry)

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "NumberActions", "MenuActions"],
			{
				"cancel": self.quit,
				"green": self.send,
				"ok": self.send,
				"red": self.quit,
				"blue": self.wakeup,
				"yellow": self.rxMonitor,
				"0":self.standbyN,
				"1":self.wakeupN,
				"7":self.active_sourceN,
				"9":self.inactive_sourceN,
				"menu": self.options,
			}, -2)

		self["key_green"] = Label(_("Send"))
		self["key_red"] = Label(_("Cancel"))
		self["key_yellow"] = Label(_("Monitor"))
		self["key_blue"] = Label(_("Wakeup TV"))

		self["ltx"] = Label(_("Tx:"))
		self["lrx"] = Label(_("Rx:"))

		self['txtext'] = Label()
		self['rxtext'] = Label()

		self.txline = 0
		self.rxline = 0

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setHdmiCec()
		assert not HdmiTest.instance, "only one HdmiCec instance is allowed!"
		HdmiTest.instance = self
		eHdmiCEC.getInstance().messageReceived.get().append(self.messageReceived)
		self.setTitle(self.setup_title + "  " + VERSION)

	def mainMenu(self):
		self.HdmiTestMenuList = []
		self.HdmiTestMenuList.append(getConfigListEntry(_("Command"), cfg.cmd))
		self.HdmiTestMenuList.append(getConfigListEntry(_("Real physical address"), cfg.realphysicaladdress))
		if cfg.realphysicaladdress.value:
			hexstring = '%04x' % eHdmiCEC.getInstance().getPhysicalAddress()
			self['address'].setText("Physical Address: " + hexstring[0] + '.' + hexstring[1] + '.' + hexstring[2] + '.' + hexstring[3])
		else:
			self.HdmiTestMenuList.append(getConfigListEntry(_("HH"), cfg.hh))
			self.HdmiTestMenuList.append(getConfigListEntry(_("HL"), cfg.hl))
			self.HdmiTestMenuList.append(getConfigListEntry(_("LH"), cfg.lh))
			self.HdmiTestMenuList.append(getConfigListEntry(_("LL"), cfg.ll))
			self['address'].setText("Physical address: %x.%x.%x.%x" % (int(cfg.hh.value), int(cfg.hl.value), int(cfg.lh.value), int(cfg.ll.value)))
		if cfg.testmode.value or int(cfg.cmd.value[:4], 0x10) in BOTH or int(cfg.cmd.value[:4], 0x10) not in BROADCAST:
			self.HdmiTestMenuList.append(getConfigListEntry(_("Addressed to"), cfg.broadcast))
		self['sendto'].setText("Send to address: 0x%x" % (self.setAddressTo()))

	def changedEntry(self):
		if self["config"].getCurrentIndex() in[0,1] or not cfg.realphysicaladdress.value and self["config"].getCurrentIndex() in[1,2,3,4,5]:
			self.refreshMenu()
		if self["config"].getCurrentIndex() == 2 or not cfg.realphysicaladdress.value and self["config"].getCurrentIndex() == 6:
			self['sendto'].setText("Send to address: 0x%x" % (self.setAddressTo()))

	def refreshMenu(self):
		self.mainMenu()
		self["config"].setList(self.HdmiTestMenuList)

	def setAddressTo(self):
		if int(cfg.cmd.value[:4], 0x10) in BROADCAST and not cfg.testmode.value:
			return 0xf
		return int(cfg.broadcast.value, 0x10)

	def setHdmiCec(self):
		if cfg.special.value in ["3","4","5"]:
			if self.queryHdmiCec() is not None:
				self.deactivateHdmiCec()
		else:
			if self.queryHdmiCec() is None:
				self.activateHdmiCec()

	def deactivateHdmiCec(self):
		idx = self.queryHdmiCec()
		if idx is not None:
			eHdmiCEC.getInstance().messageReceived.get().pop(idx)

	def activateHdmiCec(self):
		eHdmiCEC.getInstance().messageReceived.get().append(self.HDMICEC)

	def queryHdmiCec(self):
		if eHdmiCEC.getInstance().messageReceived.get().count(self.HDMICEC):
			return eHdmiCEC.getInstance().messageReceived.get().index(self.HDMICEC)
		return None

	def wakeupN(self):
		if cfg.special.value in["0","3"]:
			self.wakeup()
	def standbyN(self):
		if cfg.special.value in["0","3"]:
			self.standby()
	def active_sourceN(self):
		if cfg.special.value in["0","3"]:
			self.active_source()
	def inactive_sourceN(self):
		if cfg.special.value in["0","3"]:
			self.inactive_source()

	def wakeup(self):
		if cfg.special.value in["0","1","3","4"]:
			eHdmiCEC.getInstance().sendMessage(0, 0x04, '', 0)
	def standby(self):
		if cfg.special.value in["0","1","3","4"]:
			eHdmiCEC.getInstance().sendMessage(0, 0x36, '', 0)
	def active_source(self):
		if cfg.special.value in["0","1","3","4"]:
			data = self.address2data()
			eHdmiCEC.getInstance().sendMessage(0xf, 0x82, data, len(data))
	def inactive_source(self):
		if cfg.special.value in["0","1","3","4"]:
			data = self.address2data()
			eHdmiCEC.getInstance().sendMessage(0x00, 0x9d, data, len(data))

	def send(self):
		if self.txline > 4:
			self['txtext'].setText(self['txtext'].getText()[:self['txtext'].getText().rstrip("\n").rfind("\n")])

		data = ''
		cmd = int(cfg.cmd.value, 0x10)

		if cmd in BB:
			data = self.address2data()
		elif cmd in BBB:
			data = self.address2data(True)
		elif cmd == 0x47:
			data = os.uname()[1]
			data = data[:14]
		elif cmd in[0x720, 0x721, 0x7e0, 0x7e1, 0x8e0, 0x8e1]:
			data = str(struct.pack('B', cmd&0x1))
			cmd >>= 4
		elif cmd in[0x7a0, 0x7a1]:
			data = str(struct.pack('B', (cmd&0x1)<<7))
			cmd >>= 4
		elif cmd in[0x8d0, 0x8d1, 0x8d2]:
			data = str(struct.pack('B', cmd&0x3))
			cmd >>= 4

		address = self.setAddressTo()

		self["txtext"].setText(self.txText(cmd, address, data) + "\n" + self["txtext"].getText())
		self.txline += 1

		eHdmiCEC.getInstance().sendMessage(address, cmd, data, len(data))

	def address2data(self, full=False):
		if cfg.realphysicaladdress.value:
			physicaladdress = eHdmiCEC.getInstance().getPhysicalAddress()
			hi = int(physicaladdress/256); lo = int(physicaladdress%256)
		else:
			hi = 16*int(cfg.hh.value) + int(cfg.hl.value)
			lo = 16*int(cfg.lh.value) + int(cfg.ll.value)

		if full:
			devicetype = eHdmiCEC.getInstance().getDeviceType()
			return str(struct.pack('BBB', hi, lo, devicetype))
		return str(struct.pack('BB', hi, lo))

	def messageReceived(self, message):
		cmd = message.getCommand()
		data = 16 * '\x00'
		length = message.getData(data, len(data))
		if self.rxline > 4:
			self['rxtext'].setText(self['rxtext'].getText()[:self['rxtext'].getText().rstrip("\n").rfind("\n")])
		self["rxtext"].setText(self.rxText(cmd, data, length) + "\n" + self["rxtext"].getText())
		self.rxline += 1

	def txText(self, cmd, address, data):
		txt = "%02X" % (cmd)
		if len(data):
			if cmd in TXT:
				txt += " "
				for i in range(len(data)):
					txt += "%s" % data[i]
			else:
				for i in range(len(data)):
					txt += " " + "%02X" % ord(data[i])
		return txt + 0*" " + "\t(0x%x)" % (address)

	def rxText(self, cmd, data, length):
		txt = ''
		if cmd == 0 and length == 0:
			return " - "
		if cmd == 0x00:
			return "%02X" % ord(data[0]) + " " + abortReason[ord(data[1])]
		txt = "%02X" % (cmd)
		if cmd in TXT:
			txt +=  " "
		for i in range(length-1):
			if cmd in TXT:
				txt += "%s" % data[i]
			elif cmd == 0x90:
				txt += " " + "%02X" % ord(data[i]) + " " + powerStatus[ord(data[i])]
			elif cmd == 0x9e:
				txt += " " + "%02X" % ord(data[i]) + 3*" " + "(version: %s)" % CecVersion[ord(data[i])]
			else:
				txt += " " + "%02X" % ord(data[i])
		return txt

	def quit(self):
		# remove rx routine from list
		index = eHdmiCEC.getInstance().messageReceived.get().index(self.messageReceived)
		eHdmiCEC.getInstance().messageReceived.get().pop(index)
		# push back Components.HdmiCec to list
		if self.queryHdmiCec() is None:
			self.activateHdmiCec()
		self.close()

	def rxMonitor(self):
		index = eHdmiCEC.getInstance().messageReceived.get().index(self.messageReceived)
		eHdmiCEC.getInstance().messageReceived.get().pop(index)
		self.session.openWithCallback(self.pushBackRoutine, HdmiTestInfoScreen)

	def pushBackRoutine(self, answer=False):
		eHdmiCEC.getInstance().messageReceived.get().append(self.messageReceived)

	def options(self):
		self.session.openWithCallback(self.afterOption, HdmiTestOptions)

	def afterOption(self, answer=False):
		self.setHdmiCec()
		self.refreshMenu()
		
hdmiTest = HdmiTest(Screen)

class HdmiTestInfoScreen(Screen):
	skin = """
	<screen name="HdmiTest - incomming messages" position="center,center" size="560,505" title="HdmiTest - incomming messages" >
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />

		<widget name="key_red"    position="0,0"   size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green"  position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_blue"   position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 

		<widget name="rxtext" position="10,40" size="540,465" zPosition="1" font="Regular;18" halign="left"/>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setup_title = _("HdmiTest - Received")
		self.line = 0
		self['rxtext']=Label()

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "NumberActions"],
			{
				"cancel": self.quit,
				"red": self.quit,
				"green": self.clear,
				"yellow": hdmiTest.standby,
				"blue": hdmiTest.wakeup,
				"0":hdmiTest.standbyN,
				"1":hdmiTest.wakeupN,
				"7":hdmiTest.active_sourceN,
				"9":hdmiTest.inactive_sourceN,
			}, -2)

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label()
		self["key_yellow"] = Label(_("Standby TV"))
		self["key_blue"] = Label(_("Wakeup TV"))

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		assert not HdmiTestInfoScreen.instance, "only one HdmiCec instance is allowed!"
		HdmiTestInfoScreen.instance = self
		eHdmiCEC.getInstance().messageReceived.get().append(self.messageReceivedAll)
		self.setTitle(self.setup_title)

	def messageReceivedAll(self, message):
		if self.line > 21:
			self['rxtext'].setText(self['rxtext'].getText()[:self['rxtext'].getText().rstrip("\n").rfind("\n")])
		self["key_green"].setText("Clear")
		cmd = message.getCommand()
		data = 16 * '\x00'
		length = message.getData(data, len(data))
		opcode = ""
		if opCode.has_key(cmd):
			if cmd == 0 and length == 0:
				opcode = opCode[cmd]
			elif cmd == 0:
				opcode = "<Feature Abort>"
			else:
				opcode = "%s" % opCode[cmd]
		else:
			opcode = "%02X" % cmd
		if len(opcode) < 15:
			opcode +=  "\t"
		self["rxtext"].setText("%02d %s%s%s%s%s" % (self.line+1,opcode,"\t",hdmiTest.rxText(cmd, data, length),"\n",self["rxtext"].getText()))
		self.line += 1

	def clear(self):
		self["key_green"].setText("")
		self["rxtext"].setText("")

	def quit(self):
		index = eHdmiCEC.getInstance().messageReceived.get().index(self.messageReceivedAll)
		eHdmiCEC.getInstance().messageReceived.get().pop(index)
		self.close()

class HdmiTestOptions(Screen, ConfigListScreen):
	skin = """
	<screen name="HdmiTest - options" position="center,center" size="560,160" title="HdmiTest - options" >
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />

		<widget name="key_red"    position="0,0"   size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green"  position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_blue"   position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 

		<widget name="config" position="10,40" size="540,120" zPosition="1" itemHeight="30" font="Regular;25" scrollbarMode="showOnDemand"/>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setup_title = _("HdmiTest - options")
		
		self.HdmiTestOptionsList = []
		self.HdmiTestOptionsList.append(getConfigListEntry(_("Test mode"), cfg.testmode))
		self.HdmiTestOptionsList.append(getConfigListEntry(_("Special settings"), cfg.special))

		ConfigListScreen.__init__(self, self.HdmiTestOptionsList, session = session)

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.save,
				"red": self.cancel,
				"green": self.save,
				#"yellow": hdmiTest.standby,
				#"blue": hdmiTest.wakeup,
			}, -2)

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))

	def cancel(self):
		self.close()

	def save(self):
		self.keySave()