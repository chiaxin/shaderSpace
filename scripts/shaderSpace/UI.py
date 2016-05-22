'''
    Main User-Interface for shaderSpace Rapid Shader Workflow Tool in Maya

    Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
    E-Mail : nnnight@gmail.com
    Github : http://github.com/chiaxin
'''
# Python built-in modules
from os import listdir
from os.path import isdir, isfile, join
from functools import partial
import re

# Shader Space modules
import base
import tools
from config import optionsDefaultMaps, optionsVariableMaps
from config import kShadersList, kAboutContent, kShaderPlugins, kShaderButtons
from config import kChannelNames, kVersion, kWebsite
from config import kChannelsPanelAnn, kAssignAnn, kGammaCorrectAnn, kAutoFileAnn, kMirrorAnn
from core import isVaildName, substituteVariables, createShader, reconnectShader

# Maya modules
import maya.cmds as mc
from pymel.core import optionVar

# -----------------------------------------------
# : Read all option variables
# -----------------------------------------------
for key in optionsVariableMaps.keys():
    if not mc.optionVar(exists=optionsVariableMaps[key]):
        optionVar[optionsVariableMaps[key]] = optionsDefaultMaps[key]
gNameRuleMaps = {}
for key in ('APR', 'SNR', 'SGN', 'TEX', 'B2D', 'P2D', 'MIF'):
    try: 
        gNameRuleMaps[key] = mc.optionVar(q=optionsVariableMaps[key]).encode('ascii','ignore')
    except KeyError: 
        gNameRuleMaps[key] = optionsDefaultMaps[key].encode('ascii', 'ignore')
    except:
        mc.warning('OptionVar load error occurred')
        raise
gParameters = {}
try: 
    gParameters['BMP'] = mc.optionVar(q=optionsVariableMaps['BMP'])
except: 
    gParameters['BMP'] = optionsDefaultMaps['BMP']

gParameters['MIR'] = 0
try: 
    gParameters['IGN'] = mc.optionVar(q=optionsVariableMaps['IGN'])
except: 
    gParameters['IGN'] = int(optionsDefaultMaps['IGN'])

try: 
    gParameters['AIL'] = mc.optionVar(q=optionsVariableMaps['AIL'])
except: 
    gParameters['AIL'] = int(optionsDefaultMaps['AIL'])

try:
    gParameters['STP'] = mc.optionVar(q=optionsVariableMaps['STP'])
except:
    gParameters['STP'] = int(optionsDefaultMaps['STP'])

gShaderPresetDefinition = {}
for shader in kShadersList:
    gShaderPresetDefinition[shader] = ''

# -----------------------------------------------
# : Read option variables end
# -----------------------------------------------

def shaderSpace():
    title = 'Shader Space Tool'
    version = kVersion
    WIN = MainUI()
    UIT = MainUIT()
    MENU= MainMenu()
    NBLOCK= NamingBlock()
    OBLOCK= OptionsBlock()
    CBLOCK= ChannelsBlock()
    ABLOCK= ActionsBlock()
    BLOCKS = [NBLOCK, OBLOCK, CBLOCK, ABLOCK ]
    WIN.build(MENU, BLOCKS, UIT, title + ' ' + version)
    WIN.show()

# -----------------------------------------------
# : Main window define
# -----------------------------------------------
class MainUI(base.BaseUI):
    Win = 'shaderSpaceMainWIN'
    Frl = 'shaderSpaceMainFRL'
    width = 345
    height= 450

class MainUIT(base.BaseUIT):
    Uit = 'shaderSpaceMainUIT'

class MainMenu:
    Col = 'shaderSpaceMainMenuCol'
    Bar = 'shaderSpaceMainMenuBar'
    Ign = 'shaderSpaceIgnCheck'
    Ail = 'shaderSpaceAilCheck'
    Stp = 'shaderSpaceStpCheck'
    def build(self):
        self.Col = mc.columnLayout(self.Col)
        self.Bar = mc.menuBarLayout(self.Bar)

        mc.menu(l='File')
        mc.menuItem(l='Save',   c=lambda *args : optionVarsUpdate())
        mc.menuItem(l='Reset',  c=lambda *args : optionVarsReset())
        mc.menuItem(d=True)
        mc.menuItem(l='Export', c=lambda *args : exportSetting())
        mc.menuItem(l='Load',   c=lambda *args : loadSetting())
        mc.menuItem(d=True)
        mc.menuItem(l='Clean',  c=lambda *args : optionVarsCleanUp())

        mc.menu(l='Edit')
        mc.menuItem(l='Node Name', sm=True, to=True)
        mc.menuItem(l='Shader',         c=lambda *args : ruleSettingUI('SNR', 'Shader'))
        mc.menuItem(l='Shading Group',  c=lambda *args : ruleSettingUI('SGN', 'Shading Group'))
        mc.menuItem(l='Texture',        c=lambda *args : ruleSettingUI('TEX', 'Texture Node'))
        mc.menuItem(l='Bump2d',         c=lambda *args : ruleSettingUI('B2D', 'Bump2d'))
        mc.menuItem(l='Place2dTexture', c=lambda *args : ruleSettingUI('P2D', 'Place2dTexture'))
        mc.menuItem(l='materialInfo',   c=lambda *args : ruleSettingUI('MIF', 'Material Info'))
        mc.setParent('..', menu=True)

        self.Ign = mc.menuItem(self.Ign, l='Ignore auto path if not found', \
        cb=bool(gParameters['IGN']), c=lambda *args : self.toggleIGN())
        self.Ail = mc.menuItem(self.Ail, l='Alpha Is Luminance if outAlpha', \
        cb=bool(gParameters['AIL']), c=lambda *args : self.toggleAIL())
        self.Stp = mc.menuItem(self.Stp, l='Shared Place2dTexture', \
        cb=bool(gParameters['STP']), c=lambda *args : self.toggleSTP())

        mc.menu(l='Tools')
        mc.menuItem(l='UV Snap Shot',   c=partial(ssTools, 'uvsnapshot', 'Batch UV Snapshot'))
        mc.menuItem(l='Export Meshes',  c=partial(ssTools, 'exportMesh', 'Batch Export Meshes'))
        mc.menuItem(l='Export Shaders', c=partial(ssTools, 'exportShader', 'Export Shaders'))
        mc.menuItem(l='Create PSD',     c=partial(ssTools, 'createPsd', 'Create Photoshop File'))

        mc.menu(l='Rebuild')
        for shader in kShadersList:
            if mc.pluginInfo(kShaderPlugins[shader], q=True, loaded=True) or \
            kShaderPlugins[shader] == 'none':
                mc.menuItem(l='To ' + shader, c=partial(self.reconnect, shader))
            else:
                mc.menuItem(l='To ' + shader, en=False)

        mc.menu(l='Help')
        mc.menuItem(l='Help',  c=lambda *args : shaderSpaceHelp())
        mc.menuItem(l='About', c=lambda *args : shaderSpaceAbout())

        mc.setParent('..')
        mc.setParent('..')

    def toggleIGN(self):
        gParameters['IGN'] = int(mc.menuItem(self.Ign, q=True, cb=True))

    def toggleAIL(self):
        gParameters['AIL'] = int(mc.menuItem(self.Ail, q=True, cb=True))

    def toggleSTP(self):
        gParameters['STP'] = int(mc.menuItem(self.Stp, q=True, cb=True))

    def switchMode(self, *args):
        mc.deleteUI(MainUI.Frl, layout=True)

    def reconnect(self, *args):
        selections = [s for s in mc.ls(sl=True) if mc.nodeType(s) in kShadersList]
        if not selections:
            mc.warning('Please select one or more shaders')
            return
        all_shaders = []
        for selected in selections:
            shader, shadingGroup = reconnectShader(selected, args[0])
            print '{0} rebuild : {1} ( {2} )'.format(selected, (shader + ', ' + shadingGroup), args[0])
            all_shaders.append(shader)
        mc.select(all_shaders, r=True)

class NamingBlock(base.BaseBlock):
    Frl = 'shaderSpaceNamingFRL'
    Col = 'shaderSpaceNamingCOL'
    width = 300
    height= 135
    Label = 'Naming'
    kTextFields = ['shaderSpaceAstTF', 'shaderSpaceSdnTF', \
    'shaderSpaceUsrTF', 'shaderSpaceVerTF']
    try:
        contents = [ \
        mc.optionVar(q=optionsVariableMaps['AST']), \
        mc.optionVar(q=optionsVariableMaps['SDN']), \
        mc.optionVar(q=optionsVariableMaps['USR']), \
        mc.optionVar(q=optionsVariableMaps['VER'])]
    except:
        mc.warning('shaderSpace optionVar capture failed in Naming')
        contents = [ \
        optionsDefaultMaps['AST'] , \
        optionsDefaultMaps['SDN'] , \
        optionsDefaultMaps['USR'] , \
        optionsDefaultMaps['VER']]
        for key in ('AST', 'SDN' 'USR', 'VER'):
            mc.optionVar(remove=optionsVariableMaps[key])
            optionVar[optionsVariableMaps[key]] = optionsDefaultMaps.get(key, 'undefined')

    def content(self):
        self.Col = mc.columnLayout(self.Col)

        mc.rowLayout(nc=2)
        mc.text(l='Asset')
        self.kTextFields[0] = mc.textField(self.kTextFields[0], \
        tx=self.contents[0], cc=partial(self.save, 0))
        mc.setParent('..')

        mc.rowLayout(nc=2)
        mc.text(l='Shader')
        self.kTextFields[1] = mc.textField(self.kTextFields[1], \
        tx=self.contents[1], cc=partial(self.save, 1))
        mc.setParent('..')

        mc.rowLayout(nc=2)
        mc.text(l='User')
        self.kTextFields[2] = mc.textField(self.kTextFields[2], \
        tx=self.contents[2], cc=partial(self.save, 2))
        mc.setParent('..')

        mc.rowLayout(nc=2)
        mc.text(l='Version')
        self.kTextFields[3] = mc.textField(self.kTextFields[3], \
        tx=self.contents[3], cc=partial(self.save, 3))
        mc.setParent('..')

        mc.setParent('..')

    def save(self, *args):
        index = args[0]
        userEnter = mc.textField(self.kTextFields[index], q=True, tx=True)
        if not userEnter:
            mc.textField(self.kTextFields[index], e=True, tx=self.contents[index])
            return
        elif not isVaildName( userEnter ):
            mc.warning('Invaild Name :' + userEnter)
            mc.textField(self.kTextFields[index], e=True, tx=self.contents[index])
        else:
            self.contents[index] = userEnter

class OptionsBlock( base.BaseBlock ):
    Frl = 'shaderSpaceOptionsFRL'
    Col = 'shaderSpaceOptionsCOL'
    Label = 'Options'
    width = 300
    height= 36
    kCheckBoxs = [ 'shaderSpaceAssignCB', 'shaderSpaceGammaCB', \
    'shaderSpaceAutoCB', 'shaderSpaceMirrorCB' ]

    checks = mc.optionVar(q=optionsVariableMaps['OPT'])

    if type(checks) not in [list, tuple] or len(checks) != 4:
        mc.warning('shaderSpace optionVar capture failed of Options')
        checks = optionsDefaultMaps.get('OPT', (0, 0, 0, 0))

    def content(self):
        self.Col = mc.columnLayout(self.Col)
        mc.rowLayout(nc=4)
        self.kCheckBoxs[0] = mc.checkBox(self.kCheckBoxs[0], l='Assign', \
        v=self.checks[0], cc=partial(self.toggle, 0), ann=kAssignAnn)
        self.kCheckBoxs[1] = mc.checkBox(self.kCheckBoxs[1], l='Gamma Correct', \
        v=self.checks[1], cc=partial(self.toggle, 1), ann=kGammaCorrectAnn)
        self.kCheckBoxs[2] = mc.checkBox(self.kCheckBoxs[2], l='Auto File', \
        v=self.checks[2], cc=partial(self.toggle, 2), ann=kAutoFileAnn)
        self.kCheckBoxs[3] = mc.checkBox(self.kCheckBoxs[3], l='Mirror', \
        v=self.checks[3], cc=partial(self.toggle, 3), ann=kMirrorAnn)
        mc.setParent('..')
        mc.setParent('..')

        mc.popupMenu(parent=self.kCheckBoxs[2])
        mc.menuItem(l='Path Rule', c=partial(self.popAutoPathUI))

        mc.popupMenu(parent = self.kCheckBoxs[3])
        mc.radioMenuItemCollection()
        mc.menuItem(l='Mirror U' , rb=True,  c=partial(self.mirrorSwitch, 0))
        mc.menuItem(l='Mirror V' , rb=False, c=partial(self.mirrorSwitch, 1))
        mc.menuItem(l='Both'     , rb=False, c=partial(self.mirrorSwitch, 2))

    def popAutoPathUI(self, *args):
        ui = SubRuleUI()
        uit = SubWinUIT()
        menu= SubRuleMenu('APR')
        blocks = [SubRuleBlock('APR'), IntroBlock('APR')]
        ui.build(menu, blocks, uit, 'Auto Texture File Rule Setting')
        ui.show()

    def toggle(self, *args):
        self.checks[args[0]] = int(mc.checkBox(self.kCheckBoxs[args[0]], q=True, v=True))

    def mirrorSwitch(self, *args):
        gParameters['MIR'] = args[0]

class ChannelsBlock( base.BaseBlock ):
    Frl = 'shaderSpaceChannelsFRL'
    Col = 'shaderSpaceChannelsCOL'
    Label = 'Channel Selections'
    width = 300
    height= 100

    checkBoxs = [ \
    'ssColCB', 'ssDifCB', 'ssRouCB', \
    'ssRelCB', 'ssRlcCB', 'ssGlsCB', \
    'ssTrsCB', 'ssRfcCB', 'ssRfgCB', \
    'ssBmpCB', 'ssIncCB', 'ssOpaCB' ]

    sMenus = [ \
    'ssColMU', 'ssDifMU', 'ssRouMU', \
    'ssRelMU', 'ssRlcMU', 'ssGlsMU', \
    'ssTrsMU', 'ssRfcMU', 'ssRfgMU', \
    'ssBmpMU', 'ssIncCB', 'ssOpaCB' ]

    fMenus = [ \
    ['ssColOffMI', 'ssColMipMI', 'ssColBoxMI'\
    ,'ssColQudMI', 'ssColQurMI', 'ssColGusMI'], \
    ['ssDifOffMI', 'ssDifMipMI', 'ssDifBoxMI'\
    ,'ssDifQudMI', 'ssDifQurMI', 'ssDifGusMI'], \
    ['ssRouOffMI', 'ssRouMipMI', 'ssRouBoxMI'\
    ,'ssRouQudMI', 'ssRouQurMI', 'ssRouGusMI'], \
    ['ssRelOffMI', 'ssRelMipMI', 'ssRelBoxMI'\
    ,'ssRelQudMI', 'ssRelQurMI', 'ssRelGusMI'], \
    ['ssRlcOffMI', 'ssRlcMipMI', 'ssRlcBoxMI'\
    ,'ssRlcQudMI', 'ssRlcQurMI', 'ssRlcGusMI'], \
    ['ssGlsOffMI', 'ssGlsMipMI', 'ssGlsBoxMI'\
    ,'ssGlsQudMI', 'ssGlsQurMI', 'ssGlsGusMI'], \
    ['ssTrsOffMI', 'ssTrsMipMI', 'ssTrsBoxMI'\
    ,'ssTrsQudMI', 'ssTrsQurMI', 'ssTrsGusMI'], \
    ['ssRfcOffMI', 'ssRfcMipMI', 'ssRfcBoxMI'\
    ,'ssRfcQudMI', 'ssRfcQurMI', 'ssRfcGusMI'], \
    ['ssRfgOffMI', 'ssRfgMipMI', 'ssRfgBoxMI'\
    ,'ssRfgQudMI', 'ssRfgQurMI', 'ssRfgGusMI'], \
    ['ssBmpOffMI', 'ssBmpMipMI', 'ssBmpBoxMI'\
    ,'ssBmpQudMI', 'ssBmpQurMI', 'ssBmpGusMI'], \
    ['ssIncOffMI', 'ssIncMipMI', 'ssIncBoxMI'\
    ,'ssIncQudMI', 'ssIncQurMI', 'ssIncGusMI'], \
    ['ssOpaOffMI', 'ssOpaMipMI', 'ssOpaBoxMI'\
    ,'ssOpaQudMI', 'ssOpaQurMI', 'ssOpaGusMI'] ]

    kFILTERS = ('off', 'mipmap', 'box', 'quadratic', 'quartic', 'guassian')
    kBUMP_VALUES = (0.01, 0.02, 0.025, 0.05, 0.1, 0.5, 1)

    checks = list(optionVar[optionsVariableMaps['CCK']])
    if type(checks) not in [list, tuple] or len(checks) != 12:
        mc.warning('shaderSpace optionVar capture failed in Channels')
        checks = optionsDefaultMaps['CCK']
        optionVar(remove = optionsVariableMaps['CCK'] )
        optionVar[optionsVariableMaps['CCK']] = optionsDefaultMaps['CCK']

    shorts = list(optionVar[optionsVariableMaps['CST']])
    if type(shorts) not in [list, tuple] or len(shorts) != 12:
        mc.warning('shaderSpace optionVar capture failed in Shorts')
        shorts = optionsDefaultMaps['CST']
        optionVar(remove = optionsVariableMaps['CST'])
        optionVar[optionsVariableMaps['CST']] = optionsDefaultMaps['CST']

    filters = list(optionVar[optionsVariableMaps['CFR']])
    if type(filters) not in [list, tuple] or len(filters) != 12:
        mc.warning('shaderSpace optionVar capture failed in Filters')
        filters = optionsDefaultMaps['CFR']
        optionVar(remove = optionsVariableMaps['CFR'])
        optionVar[optionsVariableMaps['CFR']] = optionsDefaultMaps['CFR']

    def content(self):
        self.Col = mc.columnLayout(self.Col, ann = kChannelsPanelAnn)
        mc.rowLayout(nc=3, cw3=(100, 100, 100))
        self.checkBoxs[0] = mc.checkBox(self.checkBoxs[0], l=kChannelNames[0], \
        v=self.checks[0], cc=partial(self.toggle, 0))
        self.checkBoxs[1] = mc.checkBox(self.checkBoxs[1], l=kChannelNames[1], \
        v=self.checks[1], cc=partial(self.toggle, 1))
        self.checkBoxs[2] = mc.checkBox(self.checkBoxs[2], l=kChannelNames[2], \
        v=self.checks[2], cc=partial(self.toggle, 2))
        mc.setParent('..')

        mc.rowLayout(nc=3, cw3=(100, 100, 100))
        self.checkBoxs[3] = mc.checkBox(self.checkBoxs[3], l=kChannelNames[3], \
        v=self.checks[3], cc=partial(self.toggle, 3))
        self.checkBoxs[4] = mc.checkBox(self.checkBoxs[4], l=kChannelNames[4], \
        v=self.checks[4], cc=partial(self.toggle, 4))
        self.checkBoxs[5] = mc.checkBox(self.checkBoxs[5], l=kChannelNames[5], \
        v=self.checks[5], cc=partial(self.toggle, 5))
        mc.setParent('..')

        mc.rowLayout(nc=3, cw3=(100, 100, 100))
        self.checkBoxs[6] = mc.checkBox(self.checkBoxs[6], l = kChannelNames[6], \
        v=self.checks[6], cc = partial(self.toggle, 6))
        self.checkBoxs[7] = mc.checkBox(self.checkBoxs[7], l = kChannelNames[7], \
        v=self.checks[7], cc = partial(self.toggle, 7))
        self.checkBoxs[8] = mc.checkBox(self.checkBoxs[8], l = kChannelNames[8], \
        v=self.checks[8], cc = partial(self.toggle, 8))
        mc.setParent('..')

        mc.rowLayout(nc=3, cw3=(100, 100, 100))
        self.checkBoxs[9] = mc.checkBox(self.checkBoxs[9], l = kChannelNames[9], \
        v=self.checks[9], cc=partial(self.toggle, 9))
        self.checkBoxs[10] = mc.checkBox(self.checkBoxs[10], l = kChannelNames[10], \
        v=self.checks[10], cc=partial(self.toggle, 10))
        self.checkBoxs[11] = mc.checkBox(self.checkBoxs[11], l = kChannelNames[11], \
        v=self.checks[11], cc=partial(self.toggle, 11))
        mc.setParent('..')
        mc.setParent('..')

        for idx, channel in enumerate( self.checkBoxs ):
            mc.popupMenu(parent=channel)
            self.sMenus[idx] = mc.menuItem(self.sMenus[idx], \
            l=self.shorts[idx], c=partial(self.popShortChange, idx))

            mc.popupMenu(parent=channel, ctl=True)
            mc.radioMenuItemCollection()
            for n, filt in enumerate(self.kFILTERS):
                self.fMenus[idx][n] = mc.menuItem(self.fMenus[idx][n], \
                l=filt, rb=(self.filters[idx] == n), \
                c=partial(self.filterSwitch, idx, n))

        mc.popupMenu(parent=self.checkBoxs[9], alt=True)
        mc.menuItem(l='Bump Value')
        mc.menuItem(d=True)
        mc.radioMenuItemCollection()
        for m, value in enumerate(self.kBUMP_VALUES):
            mc.menuItem(l=str(value), rb=(gParameters['BMP'] == self.kBUMP_VALUES[m]), \
            c = partial(self.bumpValueSwitch, m))

    def toggle(self, *args):
        value = int( mc.checkBox( self.checkBoxs[args[0]], q = True, v = True ) )
        self.checks[args[0]] = value
        print 'The {0} channel has been switched : {1}'.format( kChannelNames[args[0]], bool(value) )

    def popShortChange(self, *args):
        ans = mc.promptDialog( t = 'Channel name', m = 'Enter short:', \
        b = [ 'OK', 'Cancel' ], db = 'OK', cb = 'Cancel', ds = 'Cancel' )
        if ans == 'Cancel': return
        short = mc.promptDialog( q = True, tx = True )
        if not isVaildName( short ):
            mc.warning('This is invaild : ' + short)
        else:
            self.shorts[ args[0] ] = short
            mc.menuItem( self.sMenus[args[0]], e = True, l = short )
            print 'The channel\'s short name has been changed : {0}'.format(short)

    def filterSwitch(self, *args):
        self.filters[ args[0] ] = args[1]
        print 'The {0} channel\'s filter has been changed : {1}'.\
        format( kChannelNames[args[0]], self.kFILTERS[args[1]] )

    def bumpValueSwitch(self, *args):
        gParameters['BMP'] = self.kBUMP_VALUES[ args[0] ]
        print 'Bump value has been changed : {0}'.format( self.kBUMP_VALUES[args[0]] )

class ActionsBlock(base.BaseBlock):
    Frl = 'shaderSpaceActionsFRL'
    Col = 'shaderSpaceActionsCOL'
    Tab = 'shaderSpaceActionsTAB'
    width = 300
    height= 160
    label = 'Shader Library'
    presetsDir = mc.internalVar(ups=True) + 'attrPresets/'
    presetUnsetColor = (0.371, 0.371, 0.371)
    presetSetColor = (0.45, 0.6, 0.68)

    def content(self):
        self.Col = mc.columnLayout( self.Col )
        createSubTab = mc.columnLayout( 'createSubTab' )
        for sd in kShaderButtons.keys():
            shaderButton = mc.button( l = kShaderButtons[sd], bgc = self.presetUnsetColor, \
            en = mc.pluginInfo( kShaderPlugins[sd], q = True, l = True ) \
            or kShaderPlugins[sd] == 'none', c = partial(self.doIt, shaderType=sd))
            presets = self.getPresets(sd)
            if presets:
                mc.popupMenu( parent = shaderButton )
                mc.radioMenuItemCollection()
                mc.menuItem( l = '-----', rb = True, c = partial( self.unsetPreset, sd, shaderButton ) )
                for preset in presets:
                    mc.menuItem( l = preset, rb = False,  c = partial( self.setPreset, sd, preset, shaderButton ) )
        mc.setParent('..')

    def getPresets(self, *args):
        presets = []
        if args[0] in kShadersList:
            searchDir = self.presetsDir + '/' + args[0]
            if isdir( searchDir ):
                presets = [ f[:-4] for f in listdir(searchDir) \
                if isfile(join(searchDir, f)) and f[-3:] == 'mel' ]
        return presets

    def setPreset(self, *args):
        gShaderPresetDefinition[args[0]] = args[1]
        print '# {0} preset has been set : {1}'.format( args[0], args[1] )
        mc.button( args[2], e = True, bgc = self.presetSetColor, l = kShaderButtons[args[0]] + ' ~' + args[1] )

    def unsetPreset(self, *args):
        gShaderPresetDefinition[args[0]] = ''
        print '# {0} preset has been set default'.format( args[0] )
        mc.button( args[1], e = True, bgc = self.presetUnsetColor, l = kShaderButtons[args[0]] )

    def doIt(self, *args, **kwargs):
        def confirm(stype):
            preset = gShaderPresetDefinition[stype]
            if preset: message = 'Create {0} ~ {1}?'.format(stype, preset)
            else: message = 'Create {0}?'.format(stype)
            if mc.confirmDialog(t='Shader Create', m=message, \
            button=['Yes','No'], db='Yes', cb='No', ds='No') == 'No':
                return False
            return True
        try:
            selections = mc.ls(sl=True)
            stype = kwargs['shaderType']
            uvMirror = -1
            if OptionsBlock.checks[3]:
                uvMirror = gParameters['MIR']
            if not confirm(stype): return
            sd, sg = createShader( \
            asset=NamingBlock.contents[0], \
            shader=NamingBlock.contents[1], \
            user=NamingBlock.contents[2], \
            version=NamingBlock.contents[3], \
            shaderType=stype, \
            preset=gShaderPresetDefinition[stype], \
            channelNames=ChannelsBlock.shorts, \
            checks=ChannelsBlock.checks, \
            filters=ChannelsBlock.filters, \
            autopathRule=gNameRuleMaps['APR'], \
            shaderRule=gNameRuleMaps['SNR'], \
            shadingGroupRule=gNameRuleMaps['SGN'], \
            textureRule=gNameRuleMaps['TEX'], \
            bump2dRule=gNameRuleMaps['B2D'], \
            place2dTextureRule=gNameRuleMaps['P2D'], \
            materialInfoRule=gNameRuleMaps['MIF'], \
            isGammaCorrect=OptionsBlock.checks[1], \
            isAutopath=OptionsBlock.checks[2], \
            isUvMirror=uvMirror,\
            bumpValue=gParameters['BMP'],\
            igroneTexIsNotExists=gParameters['IGN'],\
            isAlphaIsLum=gParameters['AIL'],\
            isSharedP2d=gParameters['STP'] )
        except:
            mc.warning('Error occurred in shader create.')
            raise

        if not sd:
            print '# Create shader process canceled'
            return

        print 'New shader has been created : {0}, {1}'.format(sd, sg)

        if selections: mc.select(selections, r=True)
        if OptionsBlock.checks[0] and selections: mc.sets(fe=sg)

        optionVarsUpdate()
# -----------------------------------------------
# : Main window end
# -----------------------------------------------

# -----------------------------------------------
# : Rule setting window define
# -----------------------------------------------
class SubRuleUI(base.BaseUI):
    Win = 'shaderSpaceRuleWIN'
    Frl = 'sahderSpaceRuleFRL'
    width = 420
    height= 200

class SubRuleBlock(base.BaseBlock):
    Frl = 'shaderSpaceRuleBlockFRL'
    Col = 'shaderSpaceRuleBlockCol'
    ruleField   = 'shaderSpacePathRuleTF'
    previewField= 'shaderSPacePathPreviewTT'
    width = 400
    height = 120

    def __init__(self, ruletype):
        self.ruletype = ruletype

    def content(self):
        self.Col = mc.columnLayout(self.Col)

        self.ruleField = mc.textField(self.ruleField, tx=gNameRuleMaps[self.ruletype])
        self.previewField = mc.text(self.previewField, l='preview')
        mc.rowLayout(nc=3)
        mc.button(l='OK', c=lambda *args : self.save())
        mc.button(l='Preview', c=lambda *args : self.preview())
        mc.button(l='Cancel', c=lambda *args : self.close())
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
        optionVar[optionsVariableMaps[self.ruletype]] = gNameRuleMaps[self.ruletype]
        print 'The rule has been stored : ' + message
        self.close()

    def close(self, *args):
        win = (self.Col).split('|')[0]
        if mc.window(win, q=True, ex=True):
            mc.deleteUI(win)

    def isVaild(self, *args):
        userinput = mc.textField(self.ruleField, q=True, tx=True)
        if len(userinput) == 0:
            mc.textField(self.ruleField, e=True, tx=gNameRuleMaps[self.ruletype])
            return False, 'Path can not be empty!'
        elif userinput.find('<channel>') != -1 and self.ruletype not in ('APR', 'TEX', 'P2D'):
            return False, '<channel> is for texture, place2dTexture node or texture path only!'
        insteadPath = substituteVariables(userinput, asset=NamingBlock.contents[0], \
        shader=NamingBlock.contents[1], user=NamingBlock.contents[2], \
        version=NamingBlock.contents[3], channel='CHANNEL')
        if not isVaildName(insteadPath) and self.ruletype != 'APR':
            return False, 'Invaild : ' + userinput
        return True, userinput

    def preview(self, *args):
        vaild, message = self.isVaild()
        if not vaild:
            mc.text(self.previewField, e=True, l=message, bgc=(0.38, 0.05, 0.05))
        else:
            mc.text(self.previewField, e=True, l=self.sub(), bgc=(0.05, 0.38, 0.05))

    def sub(self):
        rule = mc.textField(self.ruleField, q=True, tx=True)
        asset = NamingBlock.contents[0]
        shader = NamingBlock.contents[1]
        user = NamingBlock.contents[2]
        version =NamingBlock.contents[3]
        channelStringReplace = '[channel]'
        if not rule:
            return ''
        if self.ruletype in ['P2D'] and gParameters['STP']:
            channelStringReplace = 'shared'
        return substituteVariables(rule, asset=asset, shader=shader, \
        user=user, version=version, channel=channelStringReplace)

class SubRuleMenu:
    def __init__(self, ruletype):
        self.ruletype = ruletype

    def build(self):
        mc.menuBarLayout()
        mc.menu( l = 'Edit' )
        mc.menuItem( l = 'Restore', c=lambda *args : mc.textField(\
        SubRuleBlock.ruleField, e=True, tx=optionsDefaultMaps[self.ruletype]))
        mc.setParent('..')

class IntroBlock(base.BaseBlock ):
    Frl = 'shaderSpaceIntroFrl'
    Col = 'shaderSpaceIntroCol'
    width = 400
    height= 180
    def __init__(self, ruletype):
        self.ruletype = ruletype

    def content(self):
        self.Col = mc.columnLayout(self.Col)
        mc.text(l=r'All Variables :')
        mc.text(l=r'<root> : Project path')
        mc.text(l=r'<asset> : Asset Name')
        mc.text(l=r'<shader> : Shader Name')
        mc.text(l=r'<user> : User Name')
        mc.text(l=r'<version> : Version')
        mc.text(l=r'<c> : Camel-Case determine')
        if self.ruletype in ('APR', 'TEX', 'P2D'):
            mc.text(l=r'<channel> : Channel abbreviation instead')
        mc.setParent('..')

class SubWinUIT( base.BaseUIT ):
    Uit = 'shaderSpaceRuleUIT'
    def templates(self):
        mc.textField(dt=self.Uit, w=300, h=30)
        mc.button(dt=self.Uit, w=128, h=32)
        mc.text(dt=self.Uit, w=100, font='fixedWidthFont', al='left')
        mc.frameLayout(dt=self.Uit, lv=False, cl=False, cll=False, mh=5, mw=5)
        mc.columnLayout(dt=self.Uit, adj=True , rs=5, cal='center')

def ruleSettingUI(ruletype, title):
    ruleWin = SubRuleUI()
    blocks = [SubRuleBlock(ruletype), IntroBlock(ruletype)]
    menu = SubRuleMenu(ruletype)
    ruleWin.build(menu, blocks, SubWinUIT(), title)
    ruleWin.show()
# -----------------------------------------------
# : Rule setting window end
# -----------------------------------------------

# -----------------------------------------------
# : Tool functions UI & methods
# -----------------------------------------------
class ToolsUI( base.BaseUI ):
    Win = 'shaderSpaceToolsWIN'
    Frl = 'shaderSpaceToolsFRL'
    width = 420
    height= 200

class ToolsBlcok( base.BaseBlock ):
    Col = 'shaderSpaceToolsBlockCOL'
    pathFieldTFB = 'shaderSpaceToolsPathTFB'
    width = 400
    height= 180

    def browse(self):
        user_input = mc.textFieldButtonGrp(self.pathFieldTFB, q=Tru , tx=True)
        directory = mc.fileDialog2(fileMode=3, caption='Save directory choice', dir=user_input)
        if directory:
            mc.textFieldButtonGrp(self.pathFieldTFB, e=True, tx=directory[0])

class ToolsMenu:
    def build(self):
        mc.menuBarLayout()
        mc.menu(l='Help')
        mc.menuItem(l='How to use', c=lambda *args : self.help())
        mc.setParent('..')

    def help(self):
        pass

class ExportShaderBlock( ToolsBlcok ):
    modeRBG = 'shaderSpaceExportShaderModeRBG'
    exportShaderPath = mc.workspace(q=True, rd=True)
    def content(self):
        self.pathFieldTFB = mc.textFieldButtonGrp( self.pathFieldTFB, l = 'Output Path', \
        tx = self.exportShaderPath, bl = '...', cw3 = ( 80, 260, 45 ), bc = lambda *args : self.browse() )

        self.modeRBG = mc.radioButtonGrp( self.modeRBG, nrb = 2, l = 'Mode', \
        labelArray2 = ('All', 'Selected'), sl = 1, cw3 = ( 60, 60, 60 ) )

        mc.rowLayout( nc = 2, cw2=(180, 180), adjustableColumn = 1, columnAttach = (( 1, 'both', 2 ), ( 2, 'both', 2 )) )
        mc.button( l = 'Export Shaders', c = lambda *args : self.doIt() )
        mc.button( l = 'Cancel', c = lambda *args : mc.deleteUI( ToolsUI.Win ) )
        mc.setParent('..')

    def doIt(self):
        output_path = ( mc.textFieldButtonGrp( self.pathFieldTFB, q = True, tx = True ) ).replace( '\\', '/' )
        mode_idx = mc.radioButtonGrp( self.modeRBG, q = True, sl = True )
        mode = 'all'
        if mode_idx == 1:
            mode = 'all'
        elif mode_idx == 2:
            mode = 'selected'
        tools.exportShaders( output_path, mode )
        ExportShaderBlock.exportShaderPath = output_path

class ExportMeshBlock( ToolsBlcok ):
    includeTF = 'shaderSpaceExportMeshIncldeTF'
    excludeTF = 'shaderSpaceExportMeshExcludeTF'
    grpRBG    = 'shaderSpaceExportMeshMethodRBG'
    typeRBG   = 'shaderSpaceExportMeshFileTypeRBG'
    exportMeshPath = mc.workspace( q = True, rd = True )
    def content(self):
        self.pathFieldTFB = mc.textFieldButtonGrp( self.pathFieldTFB, l = 'Output Path', \
        tx = self.exportMeshPath, bl = '...', cw3 = ( 80, 260, 45 ), bc = lambda *args : self.browse() )

        self.grpRBG = mc.radioButtonGrp( self.grpRBG, nrb = 2, l = 'From', \
        labelArray2 = ('displayLayers', 'sets'), sl = 1, cw3 = ( 60, 90, 60 ) )

        self.typeRBG = mc.radioButtonGrp( self.typeRBG, nrb = 3,l = 'File Type', \
        labelArray3 = ('obj', 'ma', 'mb'), sl = 1, cw4 = ( 60, 45, 45, 45 ) )

        mc.rowLayout( nc = 2 )
        includeTF = mc.textFieldGrp( self.includeTF, l = 'Include:', cw2 = ( 60, 80 ) )
        excludeTF = mc.textFieldGrp( self.excludeTF, l = 'Exclude:', cw2 = ( 60, 80 ) )
        mc.setParent('..')
        mc.rowLayout( nc = 2, cw2=(180, 180), adjustableColumn = 1, columnAttach = (( 1, 'both', 2 ), ( 2, 'both', 2 )) )
        mc.button( l = 'Export Mesh', c = lambda *args : self.doIt() )
        mc.button( l = 'Cancel', c = lambda *args : mc.deleteUI( ToolsUI.Win ) )
        mc.setParent('..')

    def doIt(self):
        output_path =  ( mc.textFieldButtonGrp( self.pathFieldTFB, q = True, tx = True ) ).replace( '\\', '/' )
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
        grp = mc.radioButtonGrp( self.grpRBG, q = True, sl = True )
        tools.exportPolygons( output_path, output_type, exclude, include, grp )
        ExportMeshBlock.exportMeshPath = output_path

class UVSnapshotBlock( ToolsBlcok ):
    resRBG = 'shaderSpaceUVsnapshotResRBG'
    extRBG = 'shaderSpaceUVsnapshotExtRBG'
    clrRBG = 'shaderSpaceUVsnapshotColRBG'
    grpRBG = 'shaderSpaceUVsnapshotFromRBG'
    uvsnapshotPath = mc.workspace( q = True, rd = True )
    def content(self):
        self.pathFieldTFB = mc.textFieldButtonGrp( self.pathFieldTFB, l = 'Output Folder', \
        tx = self.uvsnapshotPath, bl = '...', cw3 = ( 80, 260, 45 ), bc = lambda *args : self.browse() )

        self.grpRBG = mc.radioButtonGrp( self.grpRBG, nrb = 2, l = 'From', \
        labelArray2 = ('displayLayers', 'sets'), sl = 1, cw3 = ( 60, 120, 90 ) )

        self.res_TF = mc.radioButtonGrp( self.resRBG, nrb = 3, l = 'Resolution', \
        labelArray3 = ('1024', '2048', '4096'), sl = 3, cw4 = ( 60, 80, 80, 80 ) )

        self.ext_TF = mc.radioButtonGrp( self.extRBG, nrb = 3, l = 'Extension', \
        labelArray3 = ('png', 'tif', 'tga'), sl = 1, cw4 = ( 60, 80, 80, 80 ) )

        self.clr = mc.radioButtonGrp( self.clrRBG , nrb = 3, l = 'Color', \
        labelArray3 = ('White', 'Black', 'Red'), sl = 1, cw4 = ( 60, 80, 80, 80 ) )

        mc.rowLayout( nc = 2, cw2=(180, 180), adjustableColumn = 1, columnAttach = (( 1, 'both', 2 ), ( 2, 'both', 2 )) )
        mc.button( l = 'UV SnapShot', c = lambda *args : self.doIt() )
        mc.button( l = 'Cancel', c = lambda *args : mc.deleteUI( ToolsUI.Win ) )
        mc.setParent('..')

    def doIt(self):
        output_path = ( mc.textFieldButtonGrp( self.pathFieldTFB, q = True, tx = True ) ).replace( '\\', '/' )
        resolution = 4096
        extension = 'png'
        wireframe_color = ( 1.0, 1.0, 1.0 )
        res = mc.radioButtonGrp( self.resRBG, q = True, sl = True )
        ext = mc.radioButtonGrp( self.extRBG, q = True, sl = True )
        clr = mc.radioButtonGrp( self.clrRBG, q = True, sl = True )
        grp = mc.radioButtonGrp( self.grpRBG, q = True, sl = True )

        if res ==   1: resolution = 1024
        elif res == 2: resolution = 2048
        elif res == 3: resolution = 4096

        if ext ==   1: extension = 'png'
        elif ext == 2: extension = 'tif'
        elif ext == 3: extension = 'tga'

        if clr ==   1: wireframe_color = ( 255, 255, 255 )
        elif clr == 2: wireframe_color = ( 0, 0, 0 )
        elif clr == 3: wireframe_color = ( 255, 0, 0 )

        tools.uvSnapshot( output_path, resolution, extension, wireframe_color, grp )
        UVSnapshotBlock.uvsnapshotPath = output_path

class CreatePsdBlock( ToolsBlcok ):
    uvPathTF    = 'shaderSpaceCreatePsdUVPathTF'
    psNameTF    = 'shaderSpaceCreatePsdNameTF'
    resRBG      = 'shaderSpaceCreatePsdResRBG'
    createPsdPath = mc.workspace( q = True, rd = True )
    def content(self):
        self.pathFieldTFB   = mc.textFieldButtonGrp( self.pathFieldTFB, l = 'Output Folder', \
        tx = self.createPsdPath, bl = '...', cw3 = ( 80, 260, 45 ), bc = lambda *args : self.browse() )

        self.psdfilename = mc.textFieldGrp( self.psNameTF,  l = 'PSD Name', tx = '', cw2 = ( 80, 160 ) )

        self.uvPathTF = mc.textFieldGrp( self.uvPathTF,  l = 'UV Image', tx = self.createPsdPath, cw2 = ( 80, 280 ) )

        self.resRBG = mc.radioButtonGrp( self.resRBG, nrb = 3,l = 'Resolution', \
        labelArray3 = ('1024', '2048', '4096'), sl = 3, cw4 = ( 80, 80, 80, 80 ) )
        mc.rowLayout( nc = 2, cw2=(180, 180), adjustableColumn = 1, columnAttach = (( 1, 'both', 2 ), ( 2, 'both', 2 )) )
        mc.button( l = 'Create PSD', c = lambda *args : self.doIt() )
        mc.button( l = 'Cancel', c = lambda *args : mc.deleteUI( ToolsUI.Win ) )
        mc.setParent('..')

    def doIt(self):
        output_path = ( mc.textFieldGrp( self.pathFieldTFB, q = True, tx = True ) ).replace( '\\', '/' )
        psd_name = mc.textFieldGrp( self.psNameTF, q = True, tx = True )
        output_name = '{0}/{1}.psd'.format( output_path, psd_name )
        uvsnapshot_path = ( mc.textFieldGrp( self.uvPathTF, q = True, tx = True ) ).replace( '\\', '/' )
        channels = [ ChannelsBlock.shorts[idx].encode('ascii', 'ignore') \
        for idx in range(len(kChannelNames)) if ChannelsBlock.checks[idx] ]
        res_index = mc.radioButtonGrp( self.resRBG, q = True, sl = True )
        resolution = 1024
        if res_index == 1   : resolution = 1024
        elif res_index == 2 : resolution = 2048
        elif res_index == 3 : resolution = 4096
        tools.createPhotoshopFile( output_name, uvsnapshot_path, channels, resolution )
        CreatePsdBlock.createPsdPath = output_path

def ssTools(tool, title, *args):
    win = ToolsUI()
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
    menu = ToolsMenu()
    win.build( menu, [block], SubWinUIT(), title )
    win.show()

# -----------------------------------------------
# : Tool functions UI & methods end
# -----------------------------------------------

class AboutUI( base.BaseUI ):
    Win = 'shaderSpaceAboutWIN'
    Frl = 'shaderSpaceAboutFRL'
    height= 320
    width = 300

class AboutBlock( base.BaseBlock ):
    Frl = 'shaderSpaceAboutBlockFRL'
    Col = 'shaderSpaceAboutBlockCOL'
    Label = 'About'
    height= 260
    width = 320

    def content(self):
        self.Col = mc.columnLayout( self.Col )
        mc.scrollField( ed = False, ww = True, w = 300, h = 240, text = kAboutContent )
        mc.setParent('..')
        mc.rowLayout( nc = 2 )
        mc.button( l = 'Github', w = 100, h = 30, c = lambda *args : mc.launch( web = kWebsite ) )
        mc.button( l = 'OK', w = 100, h = 30, c = lambda *args : self.close() )
        mc.setParent('..')

    def close(self):
        if mc.window( AboutUI.Win, q = True, exists = True ):
            mc.deleteUI( AboutUI.Win )

def shaderSpaceAbout(*args):
    aboutWin = AboutUI()
    blocks = [ AboutBlock() ]
    aboutWin.build( None, blocks, SubWinUIT(), 'Shader Space')
    aboutWin.show()

def shaderSpaceHelp(*args):
    pass

# -----------------------------------------------
# : Export & Load setting functions
# -----------------------------------------------
def exportSetting():
    ssoFilter = 'Shader Space Options (*.sso)'
    config_files = mc.fileDialog2( ff = ssoFilter, ds = 2, cap = 'Save configuration', \
    dir = mc.workspace( q = True, rd = True ), fm = 0 )
    if not config_files:
        return
    try:
        f = open( config_files[0], 'w' )
        f.write('# Shader Space Options\n')
        for pairs in zip( kChannelNames, ChannelsBlock.shorts ):
            f.write( 'let ' + pairs[0] + '=' + pairs[1] + '\n' )

        for idx, channel in enumerate(kChannelNames):
            f.write( 'filter ' + channel + '=' + \
            ChannelsBlock.kFILTERS[ ChannelsBlock.filters[idx] ] + '\n' )

        f.write('set Shader='          + gNameRuleMaps['SNR'] + '\n')
        f.write('set ShadingEngine='   + gNameRuleMaps['SGN'] + '\n')
        f.write('set Texture='         + gNameRuleMaps['TEX'] + '\n')
        f.write('set Bump2d='          + gNameRuleMaps['B2D'] + '\n')
        f.write('set Place2dTexture='  + gNameRuleMaps['P2D'] + '\n')
        f.write('set MaterialInfo='    + gNameRuleMaps['MIF'] + '\n')
    except:
        raise
    print('Shader space option has been saved : {0}'.format(config_files[0]))
    f.close()

def loadSetting():
    def analysisLet(para, value):
        for idx, channel in enumerate(kChannelNames):
            if para == channel:
                if not isVaildName(value):
                    print 'The {0} is invaild name, skip'.format(value)
                    return
                elif ChannelsBlock.shorts[idx] == value:
                    return
                else:
                    menuitem = ChannelsBlock.sMenus[idx]
                    if mc.menuItem( menuitem, q = True, ex = True ):
                        ChannelsBlock.shorts[idx] = value
                        mc.menuItem( ChannelsBlock.sMenus[idx], e = True, l = value )
                        print '[load] The channel short name has been changed : {0}'.format(value)
                    else:
                        print '[error] The menuItem not found, ignore : {1}'.format( menuitem )

    def analysisFilter(para, value):
        for idx, channel in enumerate( kChannelNames ):
            if para == channel:
                if value not in ChannelsBlock.kFILTERS: return

                filter_index = ChannelsBlock.kFILTERS.index(value)

                if filter_index != ChannelsBlock.filters[idx]:
                    menuitem = ChannelsBlock.fMenus[ idx ][ filter_index ]
                    if mc.menuItem( menuitem, q = True, ex = True ):
                        mc.menuItem( menuitem, e = True, rb = True )
                        ChannelsBlock.filters[idx] = filter_index
                        print '[load] The {0} channel filter has been changed : {1}'.format( channel, value )
                    else:
                        print '[error] The menuItem not found, ignore : {1}'.format( menuitem )

    def analysisSet(para, value):
        key = ''
        if para == 'Shader':            key = 'SNR'
        elif para == 'ShadingEngine':   key = 'SGN'
        elif para == 'Texture':         key = 'TEX'
        elif para == 'Bump2d':          key = 'B2D'
        elif para == 'place2dTexture':  key = 'P2D'
        elif para == 'MaterialInfo':    key = 'MIF'
        else: return
        instead_path = substituteVariables(value)
        if isVaildName(instead_path):
            gNameRuleMaps[key] = value
        else:
            print '[error] This is invaild rule : {0}, skip'.format(value)

    ssoFilter = 'Shader Space Options (*.sso)'
    config_files = mc.fileDialog2( ff = ssoFilter, ds = 2, cap = 'Load configuration', \
    dir = mc.workspace( q = True, rd = True ), fm = 1 )
    if not config_files:
        return
    try:
        count, limited = 0, 100
        syntaxParser = re.compile(r'(let|filter|set) (\w+)\s*=\s*([\w<>]+)')
        f = open( config_files[0], 'r' )
        while count < limited:
            curline = f.readline()
            if not curline: break
            parser = syntaxParser.match(curline)
            if parser:
                if parser.group(1) == 'let':
                    analysisLet( parser.group(2), parser.group(3) )
                elif parser.group(1) == 'filter':
                    analysisFilter( parser.group(2), parser.group(3) )
                elif parser.group(1) == 'set':
                    analysisSet( parser.group(2), parser.group(3) )
    except:
        raise
    print('Shader space option has been loaded. : {0}'.format( config_files[0] ) )
    f.close()
# -----------------------------------------------
# : Export & Load setting function end
# -----------------------------------------------

# -----------------------------------------------
# : Option variable functions
# -----------------------------------------------
def optionVarsReset():
    ans = mc.confirmDialog( t = 'Restore Options', m = 'Restore All Options?',
    button=( 'Yes','No' ), db = 'Yes', cb = 'No', ds = 'No' )
    if ans == 'No': return
    NamingBlock.contents[0] = optionsDefaultMaps.get('AST', 'undefined').encode('ascii', 'ignore')
    mc.textField(NamingBlock.kTextFields[0], e=True, tx=NamingBlock.contents[0])

    NamingBlock.contents[1] = optionsDefaultMaps.get('SDN', 'undefined').encode('ascii', 'ignore')
    mc.textField(NamingBlock.kTextFields[1], e=True, tx=NamingBlock.contents[1])

    NamingBlock.contents[2] = optionsDefaultMaps.get('USR', 'undefined').encode('ascii', 'ignore')
    mc.textField(NamingBlock.kTextFields[2], e=True, tx=NamingBlock.contents[2])

    NamingBlock.contents[3] = optionsDefaultMaps.get('VER', 'undefined').encode('ascii', 'ignore')
    mc.textField(NamingBlock.kTextFields[3], e=True, tx=NamingBlock.contents[3])

    for idx, check in enumerate( optionsDefaultMaps['OPT']):
        mc.checkBox( OptionsBlock.kCheckBoxs[idx], e=True, v=check)
        OptionsBlock.checks[idx] = int(check)
    for idx, short in enumerate(optionsDefaultMaps['CST']):
        mc.menuItem( ChannelsBlock.sMenus[idx], e=True, l=short)
        ChannelsBlock.shorts[idx] = short.encode('ascii', 'ignore')
    for idx, check in enumerate(optionsDefaultMaps['CCK']):
        mc.checkBox(ChannelsBlock.checkBoxs[idx], e=True, v=check)
        ChannelsBlock.checks[idx] = int(check)
    for idx, value in enumerate(optionsDefaultMaps['CFR']):
        mc.menuItem(ChannelsBlock.fMenus[idx][value], e=True, rb=True)
        ChannelsBlock.filters[idx] = int(value)
    mc.menuItem(MainMenu.Ign, e=True, cb=optionsDefaultMaps.get('IGN', True))
    mc.menuItem(MainMenu.Ail, e=True, cb=optionsDefaultMaps.get('AIL', True))
    mc.menuItem(MainMenu.Stp, e=True, cb=optionsDefaultMaps.get('STP', True))

def optionVarsUpdate():
    optionVarsCleanUp()
    optionVar[optionsVariableMaps['AST']] = NamingBlock.contents[0].encode('ascii', 'ignore')
    optionVar[optionsVariableMaps['SDN']] = NamingBlock.contents[1].encode('ascii', 'ignore')
    optionVar[optionsVariableMaps['USR']] = NamingBlock.contents[2].encode('ascii', 'ignore')
    optionVar[optionsVariableMaps['VER']] = NamingBlock.contents[3].encode('ascii', 'ignore')
    optionVar[optionsVariableMaps['OPT']] = tuple([int(e) for e in OptionsBlock.checks ])
    optionVar[optionsVariableMaps['APR']] = gNameRuleMaps['APR'].encode('ascii', 'ignore')
    optionVar[optionsVariableMaps['CST']] = tuple([e.encode( 'ascii', 'ignore' ) for e in ChannelsBlock.shorts])
    optionVar[optionsVariableMaps['CCK']] = tuple([int(e) for e in ChannelsBlock.checks])
    optionVar[optionsVariableMaps['CFR']] = tuple([int(e) for e in ChannelsBlock.filters])
    optionVar[optionsVariableMaps['BMP']] = gParameters['BMP']
    optionVar[optionsVariableMaps['SNR']] = gNameRuleMaps['SNR'].encode('ascii', 'ignore')
    optionVar[optionsVariableMaps['SGN']] = gNameRuleMaps['SGN'].encode('ascii', 'ignore')
    optionVar[optionsVariableMaps['TEX']] = gNameRuleMaps['TEX'].encode('ascii', 'ignore')
    optionVar[optionsVariableMaps['B2D']] = gNameRuleMaps['B2D'].encode('ascii', 'ignore')
    optionVar[optionsVariableMaps['P2D']] = gNameRuleMaps['P2D'].encode('ascii', 'ignore')
    optionVar[optionsVariableMaps['MIF']] = gNameRuleMaps['MIF'].encode('ascii', 'ignore')
    optionVar[optionsVariableMaps['IGN']] = int(gParameters['IGN'])
    optionVar[optionsVariableMaps['AIL']] = int(gParameters['AIL'])
    optionVar[optionsVariableMaps['STP']] = int(gParameters['STP'])

# For debug
def _printAllOptionVar():
    print optionVar[optionsVariableMaps['AST']]
    print optionVar[optionsVariableMaps['SDN']]
    print optionVar[optionsVariableMaps['USR']]
    print optionVar[optionsVariableMaps['VER']]
    print optionVar[optionsVariableMaps['OPT']]
    print optionVar[optionsVariableMaps['APR']]
    print optionVar[optionsVariableMaps['CST']]
    print optionVar[optionsVariableMaps['CCK']]
    print optionVar[optionsVariableMaps['CFR']]
    print optionVar[optionsVariableMaps['BMP']]
    print optionVar[optionsVariableMaps['SNR']]
    print optionVar[optionsVariableMaps['SGN']]
    print optionVar[optionsVariableMaps['TEX']]
    print optionVar[optionsVariableMaps['B2D']]
    print optionVar[optionsVariableMaps['P2D']]
    print optionVar[optionsVariableMaps['MIF']]
    print optionVar[optionsVariableMaps['IGN']]
    print optionVar[optionsVariableMaps['AIL']]
    print optionVar[optionsVariableMaps['STP']]

def _printAllOptions():
    print NamingBlock.contents[0]
    print NamingBlock.contents[1]
    print NamingBlock.contents[2]
    print NamingBlock.contents[3]
    print OptionsBlock.checks
    print gNameRuleMaps['APR']
    print ChannelsBlock.shorts
    print ChannelsBlock.checks
    print ChannelsBlock.filters
    print gParameters['BMP']
    print gNameRuleMaps['SNR']
    print gNameRuleMaps['SGN']
    print gNameRuleMaps['TEX']
    print gNameRuleMaps['B2D']
    print gNameRuleMaps['P2D']
    print gNameRuleMaps['MIF']
    print gParameters['IGN']
    print gParameters['AIL']
    print gParameters['STP']

def optionVarsCleanUp():
    for key in optionsVariableMaps.keys():
        if mc.optionVar(ex=optionsVariableMaps[key]):
            mc.optionVar(remove=optionsVariableMaps[key])
# -----------------------------------------------
# : Option variable functions end
# -----------------------------------------------
