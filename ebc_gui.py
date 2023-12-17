# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.0.0-0-g0efcecf)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from ebc import EBC, EbcStatus

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.app = parent
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_voltage_now = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_voltage_now, 0, wx.ALL, 5 )

		self.m_label_U = wx.StaticText( self, wx.ID_ANY, u"mV", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_label_U.Wrap( -1 )

		bSizer2.Add( self.m_label_U, 0, wx.ALL, 5 )

		self.m_current_now = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_current_now, 0, wx.ALL, 5 )

		self.m_label_I = wx.StaticText( self, wx.ID_ANY, u"mA", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_label_I.Wrap( -1 )

		bSizer2.Add( self.m_label_I, 0, wx.ALL, 5 )


		bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )

		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_connect = wx.Button( self, wx.ID_ANY, u"Connect", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_connect, 0, wx.ALL, 5 )

		self.m_button2 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button2, 0, wx.ALL, 5 )


		bSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_connect.Bind( wx.EVT_BUTTON, self.cb_conn_click)

	def cb_conn_click(self) -> None:
		self.app.connect()

	def __del__( self ):
		pass

	def update(self, d: EbcStatus) -> None:
		self.m_voltage_now = d.u
		self.m_current_now = d.i


class EbcGui(wx.App):
	def __init__(self):
		super().__init__(False)
		self.e = EBC()

		frame = MainFrame(None)
		frame.Show(True)
		self.e.set_eventhandler(frame.update)

	def connect(self) -> None:
		if self.e.is_connected:
			self.e.disconnect()
		else:
			self.e.connect()

app = EbcGui()
#start the applications
app.MainLoop()
