from functools import partial
from config import optionsDefaultMaps, optionsVariableMaps
from config import kAboutContent, kShaderPlugins, kShaderButtons
from config import kChannelNames
from core import isVaildName, substituteVariables, createShader
import string
import base
import tools
import maya.cmds as mc
import pymel.core as pm

for key in optionsVariableMaps.keys():
    if optionsVariableMaps[key] not in pm.env.optionVars:
        pm.optionVar[ optionsVariableMaps[key] ] = optionsDefaultMaps[key]
try:
    gNameRuleMaps = { \
    'APR' : mc.optionVar( q = optionsVariableMaps['APR'] ), \
    'SNR' : mc.optionVar( q = optionsVariableMaps['SNR'] ), \
    'SGN' : mc.optionVar( q = optionsVariableMaps['SGN'] ), \
    'TEX' : mc.optionVar( q = optionsVariableMaps['TEX'] ), \
    'B2D' : mc.optionVar( q = optionsVariableMaps['B2D'] ), \
    'P2D' : mc.optionVar( q = optionsVariableMaps['P2D'] ), \
    'MIF' : mc.optionVar( q = optionsVariableMaps['MIF'] ), \
    'none': '' }
except:
    gNameRuleMaps = { \
    'APR' : optionsDefaultMaps['APR'] , \
    'SNR' : optionsDefaultMaps['SNR'] , \
    'SGN' : optionsDefaultMaps['SGN'] , \
    'TEX' : optionsDefaultMaps['TEX'] , \
    'B2D' : optionsDefaultMaps['B2D'] , \
    'P2D' : optionsDefaultMaps['P2D'] , \
    'MIF' : optionsDefaultMaps['MIF'] , \
    'none': '' }
try:
    gParameters = { \
    'BMP' : mc.optionVar( q = optionsVariableMaps['BMP'] ), \
    'MIR' : 0, \
    'IGN' : bool( optionsVariableMaps['IGN'] ), \
    'AIL' : bool( optionsVariableMaps['AIL'] ) }
except:
    gParameters = { \
    'BMP' : optionsDefaultMaps['BMP'], \
    'MIR' : 0, \
    'IGN' : bool( optionsDefaultMaps['IGN'] ), \
    'AIL' : bool( optionsDefaultMaps['AIL'] ) }

def settingRestore():
    ans = mc.confirmDialog( t = 'Restore Options', m = 'Restore All Options?', 
    button=['Yes','No'], db = 'Yes', cb = 'No', ds = 'No' )
    if ans == 'No': return
    mc.textField( NamingBlock.kTextFields[0], e = True, tx = optionsDefaultMaps['AST'] )
    NamingBlock.contents[0] = optionsDefaultMaps['AST']
    mc.textField( NamingBlock.kTextFields[1], e = True, tx = optionsDefaultMaps['SDN'] )
    NamingBlock.contents[1] = optionsDefaultMaps['SDN']
    mc.textField( NamingBlock.kTextFields[2], e = True, tx = optionsDefaultMaps['USR'] )
    NamingBlock.contents[2] = optionsDefaultMaps['USR']
    mc.textField( NamingBlock.kTextFields[3], e = True, tx = optionsDefaultMaps['VER'] )
    NamingBlock.contents[3] = optionsDefaultMaps['VER']
    for idx, check in enumerate(optionsDefaultMaps['OPT']):
        mc.checkBox( OptionsBlock.kCheckBoxs[idx], e = True, v = check )
        OptionsBlock.checks[idx] = check
    for idx, short in enumerate(optionsDefaultMaps['CST']):
        mc.menuItem( ChannelsBlock.sMenus[idx], e = True, l = short )
        ChannelsBlock.shorts[idx] = short
    for idx, check in enumerate(optionsDefaultMaps['CCK']):
        mc.checkBox( ChannelsBlock.checkBoxs[idx], e = True, v = check )
        ChannelsBlock.checks[idx] = check
    for idx, value in enumerate(optionsDefaultMaps['CFR']):
        mc.menuItem( ChannelsBlock.fMenus[idx][value], e = True, rb = True )
        ChannelsBlock.filters[idx] = value
    mc.menuItem( MainMenu.Ign, e = True, cb = optionsDefaultMaps['IGN'] )
    mc.menuItem( MainMenu.Ail, e = True, cb = optionsDefaultMaps['AIL'] )

def optionVarsUpdate():
    optionVarsCleanUp()
    pm.optionVar[ optionsVariableMaps['AST'] ] = NamingBlock.contents[0]
    pm.optionVar[ optionsVariableMaps['SDN'] ] = NamingBlock.contents[1]
    pm.optionVar[ optionsVariableMaps['USR'] ] = NamingBlock.contents[2]
    pm.optionVar[ optionsVariableMaps['VER'] ] = NamingBlock.contents[3]
    pm.optionVar[ optionsVariableMaps['OPT'] ] = OptionsBlock.checks
    pm.optionVar[ optionsVariableMaps['APR'] ] = gNameRuleMaps['APR']
    pm.optionVar[ optionsVariableMaps['CST'] ] = \
    map( lambda s : s.encode('ascii', 'ignore'), ChannelsBlock.shorts )
    pm.optionVar[ optionsVariableMaps['CCK'] ] = ChannelsBlock.checks
    pm.optionVar[ optionsVariableMaps['CFR'] ] = ChannelsBlock.filters
    pm.optionVar[ optionsVariableMaps['BMP'] ] = gParameters['BMP']
    pm.optionVar[ optionsVariableMaps['SNR'] ] = gNameRuleMaps['SNR']
    pm.optionVar[ optionsVariableMaps['SGN'] ] = gNameRuleMaps['SGN']
    pm.optionVar[ optionsVariableMaps['TEX'] ] = gNameRuleMaps['TEX']
    pm.optionVar[ optionsVariableMaps['B2D'] ] = gNameRuleMaps['B2D']
    pm.optionVar[ optionsVariableMaps['P2D'] ] = gNameRuleMaps['P2D']
    pm.optionVar[ optionsVariableMaps['MIF'] ] = gNameRuleMaps['MIF']
    pm.optionVar[ optionsVariableMaps['IGN'] ] = gParameters['IGN']
    pm.optionVar[ optionsVariableMaps['AIL'] ] = gParameters['AIL']

def optionVarsCleanUp():
    for key in optionsVariableMaps.keys():
        if mc.optionVar( ex = optionsVariableMaps[ key ] ):
            mc.optionVar( remove = optionsVariableMaps[ key ] )

# -----------------------------------------------
# : Main window define
# -----------------------------------------------
class MainUI( base.BaseUI ):
    Win = 'shaderSpaceMainWIN'
    Frl = 'shaderSpaceMainFRL'
    width = 328
    height= 450

class MainUIT( base.BaseUIT ):
    Uit = 'shaderSpaceMainUIT'
    def button(self):
       mc.button( dt = self.Uit, h = 30 )

    def layout(self):
        mc.frameLayout( dt = self.Uit, cl = False, cll = False, lv = False, mh = 5, mw = 5 )
        mc.columnLayout( dt = self.Uit, adj = True , rs = 3 )

class MainMenu:
    Ign = 'shaderSpaceIgnCheck'
    Ail = 'shaderSpaceAilCheck'
    def build(self):
        mc.menuBarLayout()
        mc.menu( l = 'Edit' )
        mc.menuItem( l = 'Save Settings',   c = lambda *args : optionVarsUpdate()   )
        mc.menuItem( l = 'Restore Settings',c = lambda *args : settingRestore()     )
        mc.menuItem( l = 'Export Settings', c = lambda *args : exportSetting()      )
        mc.menuItem( l = 'Load Settings',   c = lambda *args : loadSetting()        )
        mc.menuItem( l = 'Clean Settings',  c = lambda *args : optionVarsCleanUp()  )
        mc.menu( l = 'Preferences' )
        mc.menuItem( l = 'Node Name', sm = True )
        mc.menuItem( l = 'Shader',          c = lambda *args : openRuleSetting( 'SNR', 'Shader') )
        mc.menuItem( l = 'Shading Group',   c = lambda *args : openRuleSetting( 'SGN', 'Shading Group' ) )
        mc.menuItem( l = 'Texture',         c = lambda *args : openRuleSetting( 'TEX', 'Texture Node' ) )
        mc.menuItem( l = 'Bump2d',          c = lambda *args : openRuleSetting( 'B2D', 'Bump2d' ) )
        mc.menuItem( l = 'Place2dTexture',  c = lambda *args : openRuleSetting( 'P2D', 'Place2dTexture' ) )
        mc.menuItem( l = 'materialInfo',    c = lambda *args : openRuleSetting( 'MIF', 'Material Info' ) )
        mc.setParent( '..', menu = True )
        self.Ign = mc.menuItem( self.Ign, l = 'Ignore Texture if not found', \
        cb = bool( gParameters['IGN'] ), c = lambda * args : self.toggleIGN() )
        self.Ail = mc.menuItem( self.Ail, l = 'Alpha Is Luminance in outAlpha', \
        cb = bool( gParameters['AIL'] ), c = lambda *args : self.toggleAIL() )
        mc.menu( l = 'Batch' )
        mc.menuItem( l = 'UV Snap Shot', \
        c = partial( openTools, 'uvsnapshot', 'Batch UV Snapshot from Display-Layers' ) )
        mc.menuItem( l = 'Export Meshes', \
        c = partial( openTools, 'exportMesh', 'Batch Export Meshes from Display-Layers' ) )
        mc.menuItem( l = 'Export Shaders', \
        c = partial( openTools, 'exportShader', 'Export Shaders in Scene' ) )
        mc.menuItem( l = 'Create PSD', \
        c = partial( openTools, 'createPsd', 'Create Photoshop File' ) )
        mc.menu( l = 'Help' )
        mc.menuItem( l ='Help',  c = lambda *args : openHelp() )
        mc.menuItem( l ='About', c = lambda *args : openAbout() )

    def toggleIGN(self):
        gParameters['IGN'] = mc.menuItem(self.Ign, q = True, cb = True ) 

    def toggleAIL(self):
        gParameters['AIL'] = mc.menuItem(self.Ail, q = True, cb = True )

class NamingBlock( base.BaseBlock ):
    Frl = 'NAMING_FRL'
    Col = 'NAMING_COL'
    width = 300
    height= 150
    Label = 'Naming'
    kTextFields = [ 'shaderSpaceAstTF', 'shaderSpaceSdnTF', \
    'shaderSpaceUsrTF', 'shaderSpaceVerTF' ]
    try:
        contents = [ \
        mc.optionVar( q = optionsVariableMaps['AST'] ), \
        mc.optionVar( q = optionsVariableMaps['SDN'] ), \
        mc.optionVar( q = optionsVariableMaps['USR'] ), \
        mc.optionVar( q = optionsVariableMaps['VER'] ) ]
    except:
        mc.warning('shaderSpace optionVar capture failed in Naming')
        contents = [ \
        optionsDefaultMaps['AST'] , \
        optionsDefaultMaps['SDN'] , \
        optionsDefaultMaps['USR'] , \
        optionsDefaultMaps['VER']  ]
        for key in ['AST', 'SDN' 'USR', 'VER']:
            pm.optionVar( remove = optionsVariableMaps[key] )
            pm.optionVar[ optionsVariableMaps[key] ] = optionsDefaultMaps[key]

    def content(self):
        self.Col = mc.columnLayout( self.Col )

        mc.rowLayout( nc = 2 )
        mc.text( l = 'Asset' )
        self.kTextFields[0] = mc.textField( self.kTextFields[0], \
        tx = self.contents[0], cc = partial( self.save, 0 ) )
        mc.setParent('..')

        mc.rowLayout( nc = 2 )
        mc.text( l = 'Shader' )
        self.kTextFields[1] = mc.textField( self.kTextFields[1], \
        tx = self.contents[1], cc = partial( self.save, 1 ) )
        mc.setParent('..')

        mc.rowLayout( nc = 2 )
        mc.text( l = 'User' )
        self.kTextFields[2] = mc.textField( self.kTextFields[2], \
        tx = self.contents[2], cc = partial( self.save, 2) )
        mc.setParent('..')

        mc.rowLayout( nc = 2 )
        mc.text( l = 'Version' )
        self.kTextFields[3] = mc.textField( self.kTextFields[3], \
        tx = self.contents[3], cc = partial( self.save, 3 ) )
        mc.setParent('..')

        mc.setParent('..')

    def save(self, *args):
        index = args[0]
        userEnter = mc.textField( self.kTextFields[ index ], q = True, tx = True )
        if not isVaildName( userEnter ):
            mc.warning('Invaild Name :' + userEnter)
            mc.textField( self.kTextFields[ index ], e = True, tx = self.contents[ index ] )
        else:
            self.contents[ index ] = userEnter

class OptionsBlock( base.BaseBlock ):
    Frl = 'OPTIONS_FRL'
    Col = 'OPTIONS_COL'
    width = 300
    height= 50
    Label = 'Options'
    kCheckBoxs = [ 'shaderSpaceAssignCB', 'shaderSpaceGammaCB', \
    'shaderSpaceAutoCB', 'shaderSpaceMirrorCB' ]

    checks = mc.optionVar( q = optionsVariableMaps['OPT'] )

    if type(checks) not in [list, tuple] or len(checks) != 4:
        mc.warning('shaderSpace optionVar capture failed of Options')
        checks = optionsDefaultMaps['OPT']

    def content(self):
        self.Col = mc.columnLayout( self.Col )
        mc.rowLayout( nc = 4 )
        self.kCheckBoxs[0] = mc.checkBox(self.kCheckBoxs[0], l = 'Assign', \
        v = self.checks[0], cc = partial(self.toggle, 0) )
        self.kCheckBoxs[1] = mc.checkBox(self.kCheckBoxs[1], l = 'Gamma Correct', \
        v = self.checks[1], cc = partial(self.toggle, 1) )
        self.kCheckBoxs[2] = mc.checkBox(self.kCheckBoxs[2], l = 'Auto File', \
        v = self.checks[2], cc = partial(self.toggle, 2) )
        self.kCheckBoxs[3] = mc.checkBox(self.kCheckBoxs[3], l = 'Mirror', \
        v = self.checks[3], cc = partial(self.toggle, 3) )
        mc.setParent('..')

        mc.setParent('..')

        mc.popupMenu( parent = self.kCheckBoxs[2] )
        mc.menuItem( l = 'Path Rule', c = partial( self.popAutoPathUI ) )

        mc.popupMenu( parent = self.kCheckBoxs[3] )
        mc.radioMenuItemCollection()
        mc.menuItem( l = 'Mirror U' , rb = True,  c = partial(self.mirrorSwitch, 0) )
        mc.menuItem( l = 'Mirror V' , rb = False, c = partial(self.mirrorSwitch, 1) )
        mc.menuItem( l = 'Both'     , rb = False, c = partial(self.mirrorSwitch, 2) )

    def popAutoPathUI(self, *args):
        ui = SubRuleUI()
        uit = SubWinUIT()
        menu= SubRuleMenu('APR')
        blocks = [ SubRuleBlock('APR'), IntroBlock() ]
        ui.build( menu, blocks, uit, 'Auto Texture File Rule Setting')
        ui.show()

    def toggle(self, *args):
        self.checks[ args[0] ] = mc.checkBox( self.kCheckBoxs[ args[0] ], q = True, v = True )

    def mirrorSwitch(self, *args):
        gParameters['MIR'] = args[0]

class ChannelsBlock( base.BaseBlock ):
    Frl = 'CHANNELS_FRL'
    Col = 'CHANNELS_COL'
    Label = 'Channel Selections'
    width = 300
    height= 100

    checkBoxs = [ \
    'ssColCB', 'ssBmpCB', 'ssRouCB', 'ssGlsCB', 'ssRelCB', \
    'ssRlcCB', 'ssSpcCB', 'ssTrsCB', 'ssIncCB' ]

    sMenus = [ \
    'ssColMU', 'ssBmpMU', 'ssRouMU', 'ssGlsMU', 'ssRelMU', \
    'ssRlcMU', 'ssSpcMU', 'ssTrsMU', 'ssIncMU' ]

    fMenus = [ \
    ['ssColOffMI', 'ssColMipMI', 'ssColBoxMI' \
    ,'ssColQudMI', 'ssColQurMI', 'ssColGusMI' ], \
    ['ssBmpOffMI', 'ssBmpMipMI', 'ssBmpBoxMI' \
    ,'ssBmpQudMI', 'ssBmpQurMI', 'ssBmpGusMI' ], \
    ['ssRouOffMI', 'ssRouMipMI', 'ssRouBoxMI' \
    ,'ssRouQudMI', 'ssRouQurMI', 'ssRouGusMI' ], \
    ['ssGlsOffMI', 'ssGlsMipMI', 'ssGlsBoxMI' \
    ,'ssGlsQudMI', 'ssGlsQurMI', 'ssGlsGusMI' ], \
    ['ssRelOffMI', 'ssRelMipMI', 'ssRelBoxMI' \
    ,'ssRelQudMI', 'ssRelQurMI', 'ssRelGusMI' ], \
    ['ssRlcOffMI', 'ssRlcMipMI', 'ssRlcBoxMI' \
    ,'ssRlcQudMI', 'ssRlcQurMI', 'ssRlcGusMI' ], \
    ['ssSpcOffMI', 'ssSpcMipMI', 'ssSpcBoxMI' \
    ,'ssSpcQudMI', 'ssSpcQurMI', 'ssSpcGusMI' ], \
    ['ssTrsOffMI', 'ssTrsMipMI', 'ssTrsBoxMI' \
    ,'ssTrsQudMI', 'ssTrsQurMI', 'ssTrsGusMI' ], \
    ['ssIncOffMI', 'ssIncMipMI', 'ssIncBoxMI' \
    ,'ssIncQudMI', 'ssIncQurMI', 'ssIncGusMI' ] ]

    kFILTERS = ( 'off', 'mipmap', 'box', 'quadratic', 'quartic', 'guassian' )
    kBUMP_VALUES = ( 0.01, 0.02, 0.025, 0.05, 0.1, 0.5, 1 )

    checks = list( pm.optionVar[ optionsVariableMaps[ 'CCK' ] ] )
    if type(checks) not in [ list, tuple ] or len(checks) != 9:
        mc.warning('shaderSpace optionVar capture failed in Channels')
        checks = optionsDefaultMaps['CCK']
        pm.optionVar( remove = optionsVariableMaps['CCK'] )
        pm.optionVar[ optionsVariableMaps['CCK'] ] = optionsDefaultMaps['CCK']

    shorts = list( pm.optionVar[ optionsVariableMaps[ 'CST' ] ] )
    if type(shorts) not in [ list, tuple ] or len(shorts) != 9:
        mc.warning('shaderSpace optionVar capture failed in Shorts')
        shorts = optionsDefaultMaps['CST']
        pm.optionVar( remove = optionsVariableMaps['CST'] )
        pm.optionVar[ optionsVariableMaps['CST'] ] = optionsDefaultMaps['CST']

    filters = list( pm.optionVar[ optionsVariableMaps[ 'CFR' ] ] )
    if type(filters) not in [ list, tuple ] or len(filters) != 9:
        mc.warning('shaderSpace optionVar capture failed in Filters')
        filters = optionsDefaultMaps['CFR']
        pm.optionVar( remove = optionsVariableMaps['CFR'] )
        pm.optionVar[ optionsVariableMaps['CFR'] ] = optionsDefaultMaps['CFR']

    def content(self):
        mc.columnLayout()
        mc.rowLayout( nc = 3, cw3 = (90, 90, 90) )
        self.checkBoxs[0] = mc.checkBox( self.checkBoxs[0], l = kChannelNames[0], \
        v = self.checks[0], cc = partial( self.toggle, 0 ) )
        self.checkBoxs[1] = mc.checkBox( self.checkBoxs[1], l = kChannelNames[1], \
        v = self.checks[1], cc = partial( self.toggle, 1 ) )
        self.checkBoxs[2] = mc.checkBox( self.checkBoxs[2], l = kChannelNames[2], \
        v = self.checks[2], cc = partial( self.toggle, 2 ) )
        mc.setParent('..')

        mc.rowLayout( nc = 3, cw3 = (90, 90, 90) )
        self.checkBoxs[3] = mc.checkBox( self.checkBoxs[3], l = kChannelNames[3], \
        v = self.checks[3], cc = partial( self.toggle, 3 ) )
        self.checkBoxs[4] = mc.checkBox( self.checkBoxs[4], l = kChannelNames[4], \
        v = self.checks[4], cc = partial( self.toggle, 4 ) )
        self.checkBoxs[5] = mc.checkBox( self.checkBoxs[5], l = kChannelNames[5], \
        v = self.checks[5], cc = partial( self.toggle, 5 ) )
        mc.setParent('..')

        mc.rowLayout( nc = 3, cw3 = (90, 90, 90) )
        self.checkBoxs[6] = mc.checkBox( self.checkBoxs[6], l = kChannelNames[6], \
        v = self.checks[6], cc = partial( self.toggle, 6 ) )
        self.checkBoxs[7] = mc.checkBox( self.checkBoxs[7], l = kChannelNames[7], \
        v = self.checks[7], cc = partial( self.toggle, 7 ) )
        self.checkBoxs[8] = mc.checkBox( self.checkBoxs[8], l = kChannelNames[8], \
        v = self.checks[8], cc = partial( self.toggle, 8 ) )
        mc.setParent('..')
        mc.setParent('..')

        for idx, channel in enumerate( self.checkBoxs ):
            mc.popupMenu( parent = channel )
            self.sMenus[idx] = mc.menuItem( self.sMenus[idx], \
            l = self.shorts[idx], c = partial( self.popShortChange, idx ) )

            mc.popupMenu( parent = channel, ctl = True )
            mc.radioMenuItemCollection()
            for n, filt in enumerate( self.kFILTERS ):
                self.fMenus[idx][n] = mc.menuItem( self.fMenus[idx][n], \
                l = filt, rb = ( self.filters[idx] == n ), \
                c = partial( self.filterSwitch, idx, n ) )

        mc.popupMenu( parent = self.checkBoxs[1], alt = True )
        mc.menuItem( l = 'Bump Value' )
        mc.menuItem( d = True )
        mc.radioMenuItemCollection()
        for m, value in enumerate( self.kBUMP_VALUES ):
            mc.menuItem( l = str(value), rb = ( gParameters['BMP'] == self.kBUMP_VALUES[m] ), \
            c = partial( self.bumpValueSwitch, m ) )

    def toggle(self, *args):
        value = int( mc.checkBox( self.checkBoxs[args[0]], q = True, v = True ) )
        self.checks[args[0]] = value
        print '{0} channel has been changed : {1}'.format( kChannelNames[args[0]], bool(value) )

    def popShortChange(self, *args):
        ans = mc.promptDialog( t = 'Channel name', m = 'Enter short:', \
        b = [ 'OK', 'Cancel' ], db = 'OK', cb = 'Cancel', ds = '' )
        if ans == 'Cancel': return
        short = mc.promptDialog( q = True, tx = True )
        if not isVaildName( short ):
            mc.warning('This is invaild : ' + short)
        else:
            self.shorts[ args[0] ] = short
            mc.menuItem( self.sMenus[args[0]], e = True, l = short )
            print 'The channel short name has been changed : {0}'.format(short)

    def filterSwitch(self, *args):
        self.filters[ args[0] ] = args[1]
        print '{0} channel filter has been changed : {1}'.\
        format( kChannelNames[args[0]], self.kFILTERS[args[1]] )

    def bumpValueSwitch(self, *args):
        gParameters['BMP'] = self.kBUMP_VALUES[ args[0] ]
        print 'bump value has been changed : {0}'.format( self.kBUMP_VALUES[args[0]] )

class ActionsBlock( base.BaseBlock ):
    Frl = 'ACTIONS_FRL'
    Col = 'ACTIONS_COL'
    width = 300
    height= 150
    label = 'Shader Library'

    def content(self):
        self.Col = mc.columnLayout( h = 140 )
        mc.scrollLayout( h = 120, cr = True)
        for sd in kShaderButtons.keys():
            mc.button( l = kShaderButtons[sd], 
            en = mc.pluginInfo( kShaderPlugins[sd], q = True, l = True ) \
            or kShaderPlugins[sd] == 'none', c = partial( self.doIt, sd ) )
        mc.setParent('..')
        mc.setParent('..')

    def doIt(self, *args):
        stype = args[0] # material type
        channels_name = ChannelsBlock.shorts # str in List
        nlist = NamingBlock.contents  # str in List
        channels_check= ChannelsBlock.checks # int in List
        channels_filter = ChannelsBlock.filters # int in List

        options = []
        options.append( OptionsBlock.checks[0] )
        options.append( OptionsBlock.checks[1] )
        options.append( OptionsBlock.checks[2] )
        if OptionsBlock.checks[3] == False:
            options.append( -1 )
        else:
            options.append( gParameters['MIR'] )
        options.append( gParameters['BMP'] )
        options.append( gParameters['IGN'] )
        options.append( gParameters['AIL'] )

        rules = gNameRuleMaps # Name rules in Dict 

        ans = mc.confirmDialog( t = 'Shader Create', m = '{0} create?'.format(stype), \
        button=['Yes','No'], db = 'Yes', cb = 'No', ds = 'No' )
        if ans == 'No': return

        selections = mc.ls( sl = True )

        sd, sg = createShader( nlist, stype, channels_name, \
        channels_check, options, channels_filter, rules )
        print 'New shader has been created : {0}, {1}'.format(sd, sg)
        if selections:
            mc.select( selections, r = True )
        if options[0] and selections:
            mc.sets( fe = sg )
        optionVarsUpdate()
# -----------------------------------------------
# : Main window end
# -----------------------------------------------

# -----------------------------------------------
# : Rule setting window define
# -----------------------------------------------
class SubRuleUI( base.BaseUI ):
    Win = 'shaderSpaceRuleUI'
    width = 420
    height= 200

class SubRuleBlock( base.BaseBlock ):
    Col = 'RULE_COL'
    width = 400
    height = 120
    ruleField   = 'shaderSpacePathRuleTF'
    previewField= 'shaderSPacePathPreviewTT'

    def __init__(self, ruletype):
        self.ruletype = ruletype

    def content(self):
        self.Col = mc.columnLayout( self.Col )

        self.ruleField = mc.textField( self.ruleField, tx = gNameRuleMaps[self.ruletype] )
        self.previewField = mc.text( self.previewField, l = 'preview' )
        mc.rowLayout(nc=3)
        mc.button( l = 'OK',        c = lambda *args : self.save()      )
        mc.button( l = 'Preview',   c = lambda *args : self.preview()   )
        mc.button( l = 'Cancel',    c = lambda *args : self.close()     )
        mc.setParent('..')

        mc.setParent('..')

    def save(self, *args):
        vaild, message = self.isVaild()
        if not vaild:
            self.preview()
            return
        if self.ruletype not in gNameRuleMaps:
            mc.warning('Failed to save path')
            return
        gNameRuleMaps[self.ruletype] = message
        pm.optionVar[ optionsVariableMaps[self.ruletype] ] = gNameRuleMaps[self.ruletype]
        print 'The rule has been stored : ' + message
        self.close()

    def close(self, *args):
        win = ( self.col ).split('|')[0]
        if mc.window( win, q = True, ex = True ):
            mc.deleteUI( win )

    def isVaild(self, *args):
        user_input = mc.textField( self.ruleField, q = True, tx = True )
        if len(user_input) == 0:
            mc.textField( self.ruleField, e = True, tx = gNameRuleMaps[self.ruletype] )
            return False, 'Path can not be empty!'
        elif user_input.find('<channel>') != -1 and self.ruletype not in ['APR', 'TEX']:
            #mc.textField( self.ruleField, e = True, tx = gNameRuleMaps[self.ruletype] )
            return False, '<channel> is for texture node or path only!'
        instead_path = substituteVariables( user_input, ['_', '_', '_', '_'], 'channel' )
        if not isVaildName( instead_path ) and self.ruletype != 'APR':
            return False, 'Invaild : ' + user_input
        return True, user_input

    def preview(self, *args):
        vaild, message = self.isVaild()
        if not vaild:
            mc.text( self.previewField, e = True, l = message, bgc = (0.38, 0.05, 0.05) )
        else:
            mc.text( self.previewField, e = True, l = self.sub(), bgc = (0.05, 0.38, 0.05) )

    def sub(self):
        rule = mc.textField( self.ruleField, q = True, tx = True )
        name_list = NamingBlock.contents
        if rule and name_list:
            return substituteVariables(rule, name_list, '[channel]')
        return ''

class SubRuleMenu:
    def __init__(self, ruletype):
        self.ruletype = ruletype

    def build(self):
        mc.menuBarLayout()
        mc.menu( l = 'Edit' )
        mc.menuItem( l = 'Restore', \
        c = lambda *args : mc.textField( SubRuleBlock.ruleField, e = True, \
        tx = optionsDefaultMaps[self.ruletype] ) )

class IntroBlock( base.BaseBlock ):
    Frl = 'shaderSpaceIntroFrl'
    Col = 'shaderSpaceIntroCol'
    width = 400
    height= 180

    def content(self):
        mc.columnLayout()
        mc.text( l = r'All Variabies :' )
        mc.text( l = r'<root> : Project path' )
        mc.text( l = r'<asset> : Asset Name' )
        mc.text( l = r'<shader> : Shader Name' )
        mc.text( l = r'<user> : User Name' )
        mc.text( l = r'<version> : Version' )
        mc.text( l = r'<c> : Camel-Case determine' )
        mc.text( l = r'<channel> : Channel abbreviation instead (texture only)' )
        mc.setParent('..')

class SubWinUIT( base.BaseUIT ):
    Uit = 'SubRule_UIT'
    def textField(self):
        mc.textField( dt = self.Uit, w = 300, h = 30 )

    def button(self):
        mc.button( dt = self.Uit, w = 128, h = 32 )

    def text(self):
        mc.text( dt = self.Uit, w = 100, font = 'fixedWidthFont', al = 'left' )

    def layout(self):
        mc.frameLayout( dt = self.Uit, lv = False, cl = False, cll = False, mh = 5, mw = 5 )
        mc.columnLayout( dt = self.Uit, adj = True , rs = 5, cal = 'center' )
# -----------------------------------------------
# : Rule setting window end
# -----------------------------------------------

class UtilitiesUI( base.BaseUI ):
    Win = 'SS_ToolsRule_UI'
    width = 360
    height= 200

class UtilitiesBaseBlock( base.BaseBlock ):
    width = 320
    height= 180
    col = 'UTILITIES_COL'
    pathField = 'SS_UtilitiesPath_TF'
    root = mc.workspace( q = True, rd = True )

class UtilitiesMenu:
    def build(self):
        mc.menuBarLayout()
        mc.menu( l = 'Help' )
        mc.menuItem( l = 'How to use', c = lambda *args : self.help() )

    def help(self):
        pass

class ExportShaderBlock( UtilitiesBaseBlock ):
    modeRBG = 'SS_SDFILEMODE_RBG'
    def content(self):
        self.pathField = mc.textFieldGrp( self.pathField, l = 'Output Path', tx = self.root )
        self.modeRBG = mc.radioButtonGrp( self.modeRBG, nrb = 2, l = 'Mode', \
        labelArray2 = [ 'All', 'Selected' ], sl = 1 )
        mc.button( l = 'Export Shaders', c = lambda *args : self.doIt() )

    def doIt(self):
        output_path = ( mc.textFieldGrp( self.pathField, q = True, tx = True ) ).replace( '\\', '/' )
        mode_idx = mc.radioButtonGrp( self.modeRBG, q = True, sl = True )
        mode = 'all'
        if mode_idx == 1:
            mode = 'all'
        elif mode_idx == 2:
            mode = 'selected'
        tools.exportShaders( output_path, mode )

class ExportMeshBlock( UtilitiesBaseBlock ):
    includeTF = 'SS_INCLUDE_TF'
    excludeTF = 'SS_EXCLUDE_TF'
    typeRBG   = 'SS_FILETYPE_RBG'
    def content(self):
        self.pathField = mc.textFieldGrp( self.pathField, l = 'Output Path', tx = self.root )
        self.typeRBG = mc.radioButtonGrp( self.typeRBG, nrb = 3,l = 'File Type', \
        labelArray3=['obj', 'ma', 'mb'], sl = 0 )
        includeTF = mc.textFieldGrp( self.includeTF, l = 'Include:', cw2 = ( 60, 120 ) )
        excludeTF = mc.textFieldGrp( self.excludeTF, l = 'Exclude:', cw2 = ( 60, 120 ) )
        mc.button( l = 'Export Mesh', c = lambda *args : self.doIt() )

    def doIt(self):
        output_path =  ( mc.textFieldGrp( self.pathField, q = True, tx = True ) ).replace( '\\', '/' )
        output_type = 'obj'
        filetype = mc.radioButtonGrp( self.typeRBG, q = True, sl = True )
        if filetype == 1:
            output_type = 'obj'
        elif filetype == 2:
            output_type = 'ma'
        elif filetype == 3:
            output_type = 'mb'
        else:
            mc.warning('Wrong file type')
            return
        exclude = mc.textFieldGrp( self.excludeTF, q = True, tx = True )
        include = mc.textFieldGrp( self.includeTF, q = True, tx = True )
        tools.exportPolygons( output_path, output_type, exclude, include )

class UVSnapshotBlock( UtilitiesBaseBlock ):
    resRBG = 'SS_UVSS_RES_RBG'
    extRBG = 'SS_UVSS_EXT_RBG'
    clrRBG = 'SS_UVSS_CLR_RBG'
    def content(self):
        self.col = mc.columnLayout( self.col )
        self.pathField = mc.textFieldGrp( self.pathField, l = 'Output Folder', tx = self.root )
        self.res_TF = mc.radioButtonGrp( self.resRBG, nrb = 3, l = 'Resolution', \
        labelArray3=['1024', '2048', '4096'], sl = 3 )
        self.ext_TF = mc.radioButtonGrp( self.extRBG, nrb = 3, l = 'Extension', \
        labelArray3=['png', 'tif', 'tga'], sl = 1 )
        self.clr = mc.radioButtonGrp( self.clrRBG , nrb = 3, l = 'Color', \
        labelArray3=['White', 'Black', 'Red'], sl = 1 )
        mc.button( l = 'UV SnapShot', c = lambda *args : self.doIt() )
        mc.setParent('..')

    def doIt(self):
        output_path = ( mc.textFieldGrp( self.pathField, q = True, tx = True ) ).replace( '\\', '/' )
        resolution = 4096
        extension = 'png'
        wireframe_color = [ 1.0, 1.0, 1.0 ]
        res = mc.radioButtonGrp( self.resRBG, q = True, sl = True )
        ext = mc.radioButtonGrp( self.extRBG, q = True, sl = True )
        clr = mc.radioButtonGrp( self.clrRBG, q = True, sl = True )
        if res ==   1: resolution = 1024
        elif res == 2: resolution = 2048
        elif res == 3: resolution = 4096
        else: return
        if ext ==   1: extension = 'png'
        elif ext == 2: extension = 'tif'
        elif ext == 3: extension = 'tga'
        else: return
        if clr ==   1: wireframe_color = [ 255, 255, 255 ]
        elif clr == 2: wireframe_color = [ 0, 0, 0 ]
        elif clr == 3: wireframe_color = [ 255, 0, 0 ]
        else: return
        tools.uvSnapshot( output_path, resolution, extension, wireframe_color )

class CreatePsdBlock( UtilitiesBaseBlock ):
    uvPathTF    = 'SS_UVPATH_TF'
    psNameTF    = 'SS_PSFILE_TF'
    resRB       = 'SS_PSDRES_RB'
    def content(self):
        self.pathField   = mc.textFieldGrp( self.pathField, l = 'Output Folder', tx = self.root )
        self.psdfilename = mc.textFieldGrp( self.psNameTF,  l = 'PSD File', tx = '' )
        self.uvPathTF    = mc.textFieldGrp( self.uvPathTF,  l = 'UV Image', tx = self.root )
        self.resRB = mc.radioButtonGrp( self.resRB, nrb = 3,l = 'Resolution', \
        labelArray3=['1024', '2048', '4096'], sl = 3 )
        mc.button( l = 'Create PSD', c = lambda *args : self.doIt() )

    def doIt(self):
        output_path = ( mc.textFieldGrp( self.pathField, q = True, tx = True ) ).replace( '\\', '/' )
        psd_name = mc.textFieldGrp( self.psNameTF, q = True, tx = True )
        output_name = '{0}/{1}.psd'.format( output_path, psd_name )
        uvsnapshot_path = ( mc.textFieldGrp( self.uvPathTF, q = True, tx = True ) ).replace( '\\', '/' )
        channels = [ ChannelsBlock.shorts[idx].encode('ascii', 'ignore') \
        for idx in range(len(kChannelNames)) if ChannelsBlock.checks[idx] ]
        res_index = mc.radioButtonGrp( self.resRB, q = True, sl = True )
        resolution = 1024
        if res_index == 1   : resolution = 1024
        elif res_index == 2 : resolution = 2048
        elif res_index == 3 : resolution = 4096
        tools.createPhotoshopFile( output_name, uvsnapshot_path, channels, resolution )

class AboutUI( base.BaseUI ):
    Win = 'SDSE_ABOUT_WIN'
    height= 280
    width = 300

class AboutBlock( base.BaseBlock ):
    height= 240
    width = 300
    label = 'About'
    def content(self):
        mc.columnLayout()
        mc.scrollField( ed = False, ww = True, w = 280, h = 210, text = kAboutContent )
        mc.button( l = 'OK', w = 120, h = 30, c = lambda *args : self.close() )
        mc.setParent('..')

    def close(self):
        if mc.window( AboutUI.Win, q = True, exists = True ):
            mc.deleteUI( AboutUI.Win )

def openRuleSetting(ruletype, title):
    ruleWin = SubRuleUI()
    blocks = [ SubRuleBlock(ruletype), IntroBlock() ]
    menu = SubRuleMenu(ruletype)
    ruleWin.build( menu, blocks, SubWinUIT(), title )
    ruleWin.show()

def openAbout(*args):
    aboutWin = AboutUI()
    blocks = [ AboutBlock() ]
    aboutWin.build( None, blocks, SubWinUIT(), 'Shader Space')
    aboutWin.show()

def openHelp(*args):
    pass

def exportSetting():
    ssoFilter = 'Shader Space Options (*.sso)'
    config_files = mc.fileDialog2( ff = ssoFilter, ds = 2, cap = 'Save configuration', \
    dir = mc.workspace( q = True, rd = True ), fm = 0 )
    if not config_files:
        return
    try:
        f = open( config_files[0], 'w' )
        f.write('## Shader Space Options\n')
        for pairs in zip( kChannelNames, ChannelsBlock.shorts ):
            f.write( pairs[0] + '->' + pairs[1] + '\n' )
        for idx, channel in enumerate(kChannelNames):
            f.write( channel + ':' + ChannelsBlock.kFILTERS[ ChannelsBlock.filters[idx] ] + '\n' )
        f.write( 'Shader:' + gNameRuleMaps['SNR'] + '\n')
        f.write( 'ShadingEngine:' + gNameRuleMaps['SGN'] + '\n')
        f.write( 'Texture:' + gNameRuleMaps['TEX'] + '\n')
        f.write( 'Bump2d:' + gNameRuleMaps['B2D'] + '\n')
        f.write( 'Place2dTexture:' + gNameRuleMaps['P2D'] + '\n' )
        f.write( 'MaterialInfo:' + gNameRuleMaps['MIF'] + '\n' )
        f.write( 'BumpDepth:' + str(gParameters['BMP']) + '\n' )
    except:
        raise
    print('Shader space option has been saved. : {0}'.format( config_files[0] ) )
    f.close()

def loadSetting():
    pass

def openTools(tool, title, *args):
    win = UtilitiesUI()
    if tool == 'uvsnapshot':
        block = UVSnapshotBlock()
    elif tool == 'exportMesh':
        block = ExportMeshBlock()
    elif tool == 'exportShader':
        block = ExportShaderBlock()
    elif tool == 'createPsd':
        block = CreatePsdBlock()
    else:
        mc.warning('Unknow tool : {1}'.format( tool ))
    menu = UtilitiesMenu()
    win.build( menu, [block], SubWinUIT(), title )
    win.show()

