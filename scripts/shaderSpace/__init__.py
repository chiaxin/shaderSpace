import UI

SS_WIN = UI.MainUI()
SS_UIT = UI.MainUIT()
SS_MENU= UI.MainMenu()
SS_NBLOCK= UI.NamingBlock()
SS_OBLOCK= UI.OptionsBlock()
SS_CBLOCK= UI.ChannelsBlock()
SS_ABLOCK= UI.ActionsBlock()
SS_BLOCKS = [ SS_NBLOCK, SS_OBLOCK, SS_CBLOCK, SS_ABLOCK ]
SS_WIN.build( SS_MENU, SS_BLOCKS, SS_UIT, 'Shader Space Tool v 0.2.3' )
SS_WIN.show()
