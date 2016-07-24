'''
==========================================================
The UI in shaderSpace Rapid Shader Workflow Tool in Maya
//////////////////////////////////////////////////////////
Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
E-Mail : nnnight@gmail.com
Github : http://github.com/chiaxin
==========================================================
'''
import copy
import sys
import pickle
from os import listdir
from os.path import isfile, isdir, splitext
from PySide import QtGui, QtCore
from shiboken import wrapInstance
from functools import partial
from math import ceil
import maya.cmds as mc
import maya.OpenMayaUI as omui
from pymel.all import optionVar
from config import *
from core import createShader
from tools import uvSnapshot, exportPolygons
from tools import exportShaders, createPhotoshopFile

###############################################################
# User options dictionary
###############################################################
gInitialOptions = dict()
for optVar in kDefaultMappings.keys():
    if not mc.optionVar(exists=optVar):
        gInitialOptions[optVar] = copy.deepcopy(kDefaultMappings[optVar])
    else:
        buff = mc.optionVar(q=optVar)
        if type(buff) != type(kDefaultMappings[optVar]):
            print '# OptionVar NOT MATCH :', optVar
            gInitialOptions[optVar] = copy.deepcopy(kDefaultMappings[optVar])
        elif isinstance(kDefaultMappings[optVar], list) \
        and len(buff) != len(kDefaultMappings[optVar]):
            gInitialOptions[optVar] = copy.deepcopy(kDefaultMappings[optVar])
        else:
            gInitialOptions[optVar] = mc.optionVar(q=optVar)
gShaderPreset = 'No Preset'
###############################################################
# Validator
###############################################################
gLegalMayaNodeName = QtGui.QRegExpValidator(
    QtCore.QRegExp(r'\w+'))

# Without illegal window fine name char and space
gLegalWindowFileName = QtGui.QRegExpValidator(
    QtCore.QRegExp('^[^\/\\\:\*\?\"\<\>\| ]+$'))

###############################################################
# Custom slot
###############################################################
@QtCore.Slot(str, int, str)
def updateOptions(optVar, index, value):
    global gInitialOptions
    if not gInitialOptions.has_key(optVar):
        return
    try:
        if optVar.endswith('StrOptVars'):
            buff = gInitialOptions[optVar]
            buff[index] = value
        elif optVar.endswith('StrOptVar'):
            gInitialOptions[optVar] = value
        elif optVar.endswith('IntOptVar'):
            if value in ('True', 'False'):
                gInitialOptions[optVar] = int(value == 'True')
            else:
                gInitialOptions[optVar] = int(value)
        elif optVar.endswith('IntOptVars'):
            buff = gInitialOptions[optVar]
            buff[index] = int(value)
        elif optVar.endswith('FloatOptVar'):
            gInitialOptions[optVar] = float(value)
    except:
        raise

def _getMayaMainWin():
    '''Get Maya main window using OpenMayaUI.MQtUtil'''
    pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(long(pointer), QtGui.QWidget)

def _shaderGenerate():
    global gInitialOptions, gShaderPreset
    shader, shadingGroup = \
    createShader(preset=gShaderPreset, **gInitialOptions)
    if shader:
        print shader, shadingGroup, ' has been created.'

class ShaderSpaceMainWin(QtGui.QMainWindow):
    '''Shader Space Main Window'''
    sender = QtCore.Signal(str, int, str)
    def __init__(self, parent=_getMayaMainWin()):
        super(ShaderSpaceMainWin, self).__init__(parent)
        self.sender.connect(updateOptions)
        # Set title
        self.setWindowTitle('Shader Space v'+kVersion)
        # Set title icon
        icon = mc.internalVar(userBitmapsDir=True)+'shaderSpace.png'
        if isfile(icon):
            self.setWindowIcon(QtGui.QIcon(icon))
        # Initial
        self.centralWin = ShaderSpaceCentral()
        self.setCentralWidget(self.centralWin)
        self.resize(self.minimumSizeHint())
        # Actions
        save_action = QtGui.QAction('&Save Settings', self)
        load_action = QtGui.QAction('&Load Settings', self)
        reset_action = QtGui.QAction('&Reset Settings', self)
        lock_action = QtGui.QAction('&Lock Settings', self, checkable=True)
        help_action = QtGui.QAction('&Help', self)
        about_action= QtGui.QAction('&About', self)
        # Menus
        file_menu = self.menuBar().addMenu('&File')
        help_menu = self.menuBar().addMenu('&Help')
        file_menu.addAction(save_action)
        file_menu.addAction(load_action)
        file_menu.addAction(reset_action)
        file_menu.addAction(lock_action)
        help_menu.addAction(help_action)
        help_menu.addAction(about_action)
        # Set actions
        withLocked = bool(
            gInitialOptions['shaderSpaceSettingsLockedIntOptVar'])
        lock_action.setChecked(withLocked)
        if withLocked:
            self._lockSettings(True)
        # Connect
        save_action.triggered.connect(self._dumpSave)
        load_action.triggered.connect(self._dumpLoad)
        reset_action.triggered.connect(self._resetSettings)
        help_action.triggered.connect(self._help)
        about_action.triggered.connect(self._about)
        lock_action.toggled.connect(self._lockSettings)
        lock_action.toggled.connect(
            lambda state: self.sender.emit(
                'shaderSpaceSettingsLockedIntOptVar', 0, str(state)))

    def closeEvent(self, event):
        self._saveOptionVars()
        event.accept()

    def _lockSettings(self, triggered):
        settingsWidget = self.centralWin.tab.widget(1)
        if triggered:
            settingsWidget.setEnabled(False)
        else:
            settingsWidget.setEnabled(True)

    def _help(self):
        dialog = HelpDialog()
        dialog.show()

    def _about(self):
        dialog = AboutDialog()
        dialog.show()

    def _saveOptionVars(self):
        global gInitialOptions
        for var, value in gInitialOptions.items():
            optionVar[var] = value

    def _resetSettings(self):
        msgbox = QtGui.QMessageBox()
        msgbox.setText('<h3>The settings has been reset.</h3>')
        msgbox.setInformativeText('Do you want to reset?')
        msgbox.setStandardButtons(
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        msgbox.setDefaultButton(QtGui.QMessageBox.Cancel)
        ret = msgbox.exec_()
        if ret == QtGui.QMessageBox.Cancel:
            return
        gInitialOptions['shaderSpaceNodeNameRuleStrOptVars'] = \
            copy.deepcopy(
                kDefaultMappings['shaderSpaceNodeNameRuleStrOptVars'])
        gInitialOptions['shaderSpaceAutoPathRuleStrOptVar'] = \
            copy.deepcopy(
                kDefaultMappings['shaderSpaceAutoPathRuleStrOptVar'])
        gInitialOptions['shaderSpaceAbbreviationsStrOptVars'] = \
            copy.deepcopy(
                kDefaultMappings['shaderSpaceAbbreviationsStrOptVars'])
        self._reloadWidget(1)

    def _reloadWidget(self, idx):
        withEnabled = self.centralWin.tab.widget(idx).isEnabled()
        self.centralWin.resetSettingWidget()
        self.centralWin.tab.widget(idx).setEnabled(withEnabled)

    def _dumpSave(self):
        global gInitialOptions
        data_file, fl = QtGui.QFileDialog.getSaveFileName(
            self, 'Save settings',
            mc.workspace(q=True, rootDirectory=True), 'spk (*.spk)')
        if not data_file:
            return
        dumpDataSet = []
        dumpDataSet.append(
            gInitialOptions['shaderSpaceNodeNameRuleStrOptVars'])
        dumpDataSet.append(
            gInitialOptions['shaderSpaceAutoPathRuleStrOptVar'])
        dumpDataSet.append(
            gInitialOptions['shaderSpaceAbbreviationsStrOptVars'])
        try:
            io_file = open(data_file, 'wb')
        except:
            raise
        else:
            for dumpData in dumpDataSet:
                pickle.dump(dumpDataSet, io_file)
        finally:
            io_file.close()

    def _dumpLoad(self):
        global gInitialOptions
        data_file, fl = QtGui.QFileDialog.getOpenFileName(
            self, 'Load settings',
            mc.workspace(q=True, rootDirectory=True), 'spk (*.spk)')
        if not data_file:
            return
        try:
            io_file = open(data_file, 'rb')
            dump_buff = pickle.load(io_file)
            nodeNameRuleBuff = dump_buff[0]
            autoPathRuleBuff = dump_buff[1]
            abbreviationsBuff = dump_buff[2]
        except:
            raise
        else:
            gInitialOptions['shaderSpaceNodeNameRuleStrOptVars'] = \
                nodeNameRuleBuff
            gInitialOptions['shaderSpaceAutoPathRuleStrOptVar'] = \
                autoPathRuleBuff
            gInitialOptions['shaderSpaceAbbreviationsStrOptVars'] = \
                abbreviationsBuff
            self._reloadWidget(1)
        finally:
            io_file.close()

class ShaderSpaceCentral(QtGui.QWidget):
    '''Main window central'''
    def __init__(self, parent=None):
        super(ShaderSpaceCentral, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # Widgets
        self.createWidget = ShaderSpaceCreateWin()
        self.settingWidget = ShaderSpaceSettingWin()
        self.toolsWidget = ShaderSpaceToolsWin()
        # Tab
        self.tab = QtGui.QTabWidget()
        self.tab.addTab(self.createWidget, 'Creation')
        self.tab.addTab(self.settingWidget, 'Settings')
        self.tab.addTab(self.toolsWidget, 'Tools')
        # Layouts
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tab)
        self.setLayout(layout)

    def resetSettingWidget(self):
        self.tab.removeTab(1)
        self.settingWidget.deleteLater()
        self.settingWidget = ShaderSpaceSettingWin()
        self.tab.insertTab(1, self.settingWidget, 'Settings')
        self.tab.setCurrentIndex(1)

class ShaderSpaceCreateWin(QtGui.QWidget):
    '''Shader Space Creation Page'''
    # Signal object
    sender = QtCore.Signal(str, int, str)
    _presetsDir = mc.internalVar(ups=True)+'attrPresets/'
    def __init__(self, parent=None):
        super(ShaderSpaceCreateWin, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # set connect
        self.sender.connect(updateOptions)
        grid = QtGui.QGridLayout()
        grid.addWidget(self.buildNamingTextField(), 0, 0)
        grid.addWidget(self.buildOptionsComboBoxs(), 0, 1)
        grid.addWidget(self.buildChannelCheckBoxs(), 1, 0)
        grid.addWidget(self.buildValuesControllers(), 1, 1)
        grid.addWidget(self.buildShaderComboBoxs(), 2, 0)
        grid.addWidget(self.buildExecuteButtons(), 2, 1)
        self.setLayout(grid)

    def buildNamingTextField(self):
        global gInitialOptions
        names = copy.deepcopy(gInitialOptions['shaderSpaceNameStrOptVars'])
        # Component
        assetLe = QtGui.QLineEdit(names[0])
        assetLe.setMinimumHeight(24)
        shaderLe = QtGui.QLineEdit(names[1])
        shaderLe.setMinimumHeight(24)
        userLe = QtGui.QLineEdit(names[2])
        userLe.setMinimumHeight(24)
        versionLe = QtGui.QLineEdit(names[3])
        versionLe.setMinimumHeight(24)
        # Tip
        assetLe.setToolTip('This field will replaced by <asset> variable')
        shaderLe.setToolTip('This field will replaced by <shader> variable')
        userLe.setToolTip('This field will replaced by <user> variable')
        versionLe.setToolTip('This field will replaced by <version> variable')
        # Set validator
        assetLe.setValidator(gLegalMayaNodeName)
        shaderLe.setValidator(gLegalMayaNodeName)
        userLe.setValidator(gLegalMayaNodeName)
        versionLe.setValidator(gLegalMayaNodeName)
        # Layout
        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel('Asset'), 0, 0)
        grid.addWidget(assetLe, 0, 1)
        grid.addWidget(QtGui.QLabel('Shader'), 1, 0)
        grid.addWidget(shaderLe, 1, 1)
        grid.addWidget(QtGui.QLabel('User'), 2, 0)
        grid.addWidget(userLe, 2, 1)
        grid.addWidget(QtGui.QLabel('Version'), 3, 0)
        grid.addWidget(versionLe, 3, 1)
        groupBox = QtGui.QGroupBox('Name')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        groupBox.setLayout(grid)
        # Connet
        assetLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceNameStrOptVars',
                0, text))
        shaderLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceNameStrOptVars',
                1, text))
        userLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceNameStrOptVars',
                2, text))
        versionLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceNameStrOptVars',
                3, text))
        assetLe.textEdited.connect(self._checkEmpty)
        shaderLe.textEdited.connect(self._checkEmpty)
        userLe.textEdited.connect(self._checkEmpty)
        versionLe.textEdited.connect(self._checkEmpty)
        return groupBox

    def buildChannelCheckBoxs(self):
        global kChannelList, gInitialOptions
        checks = copy.deepcopy(
            gInitialOptions['shaderSpaceChannelsIntOptVars'])
        grid = QtGui.QGridLayout()
        # Counter grid array number
        numOfChannels = len(kChannelList)
        total_col = int(ceil(float(numOfChannels) / 3))
        for col in range(total_col):
            for row in range(3):
                index = (col*3) + (row%3)
                if index >= numOfChannels:
                    continue
                if checks[index]:
                    state = QtCore.Qt.CheckState.Checked
                else:
                    state = QtCore.Qt.CheckState.Unchecked
                checkBox = QtGui.QCheckBox(kChannelList[index])
                checkBox.setCheckState(state)
                checkBox.stateChanged.connect(
                    lambda state, index=index: self.sender.emit(
                        'shaderSpaceChannelsIntOptVars', index, str(state)))
                grid.addWidget(checkBox, col, row)
        groupBox = QtGui.QGroupBox('Channels')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        groupBox.setLayout(grid)
        return groupBox

    def buildOptionsComboBoxs(self):
        global gInitialOptions
        options = copy.deepcopy(
            gInitialOptions['shaderSpaceOptionIntOptVars'])
        # Component
        assignCbb = QtGui.QComboBox()
        assignCbb.addItem('Do not assign anything')
        assignCbb.addItem('Assign selected objects')
        assignCbb.setCurrentIndex(options[0])
        assignCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit('shaderSpaceOptionIntOptVars',
                0, str(idx)))
        gcCbb = QtGui.QComboBox()
        gcCbb.addItem('Do not gamma correct')
        gcCbb.addItem('Make gamma correct')
        gcCbb.setCurrentIndex(options[1])
        gcCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit('shaderSpaceOptionIntOptVars',
                1, str(idx)))
        afpCbb = QtGui.QComboBox()
        afpCbb.addItem('Auto fill texture path')
        afpCbb.addItem('Auto fill path if exists')
        afpCbb.addItem('Do not auto fill path')
        afpCbb.setCurrentIndex(options[2])
        afpCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit('shaderSpaceOptionIntOptVars',
                2, str(idx)))
        mUvCbb = QtGui.QComboBox()
        mUvCbb.addItem('Do not mirror UV')
        mUvCbb.addItem('Mirror U')
        mUvCbb.addItem('Mirror V')
        mUvCbb.addItem('Mirror both')
        mUvCbb.setCurrentIndex(options[3])
        mUvCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit('shaderSpaceOptionIntOptVars',
                3, str(idx)))
        sP2dCbb = QtGui.QComboBox()
        sP2dCbb.addItem('Share place2dTexture for each')
        sP2dCbb.addItem('Do not share place2dTexture')
        sP2dCbb.setCurrentIndex(options[4])
        sP2dCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit('shaderSpaceOptionIntOptVars',
                4, str(idx)))
        # Tip
        assignCbb.setToolTip('Assign shader for objects after create')
        gcCbb.setToolTip('Make color management in texture')
        afpCbb.setToolTip('Auto fill texture path name when create')
        mUvCbb.setToolTip('Toggle mirror UV parameter in place2dTexture')
        sP2dCbb.setToolTip('The place2dTexture node is only one or multiple')
        # Layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(assignCbb)
        layout.addWidget(gcCbb)
        layout.addWidget(afpCbb)
        layout.addWidget(mUvCbb)
        layout.addWidget(sP2dCbb)
        groupBox = QtGui.QGroupBox('Options')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        groupBox.setLayout(layout)
        return groupBox

    def buildValuesControllers(self):
        global gInitialOptions
        bvValidator = QtGui.QRegExpValidator(
            QtCore.QRegExp(r'(0|1)\.\d{1,3}'))
        filterIndex = gInitialOptions['shaderSpaceFilterTypeIntOptVar']
        bumpValue = gInitialOptions['shaderSpaceBumpValueFloatOptVar']
        # Component
        bumpValueLe = QtGui.QLineEdit(str(bumpValue))
        bumpValueLe.setMaximumWidth(60)
        bumpValueLe.setValidator(bvValidator)
        filterCbb = QtGui.QComboBox()
        filterCbb.addItems(
            ('off', 'Mipmap', 'Box', 'Quadratic', 'Quartic', 'Gaussian'))
        filterCbb.setCurrentIndex(filterIndex)
        ailCb = QtGui.QCheckBox()
        ail_state = QtCore.Qt.CheckState.Unchecked
        if gInitialOptions['shaderSpaceAlphaIsLuminanceIntOptVar']:
            ail_state = QtCore.Qt.CheckState.Checked
        ailCb.setCheckState(ail_state)
        # Tip
        bumpValueLe.setToolTip('Set bump value')
        filterCbb.setToolTip('Set texture\'s filter type')
        ailCb.setToolTip(
            'If on, texture node\'s alphaIsLuminance will be on if outAlpha')
        # Layout
        groupBox = QtGui.QGroupBox('Values')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel('Bump Value'), 0, 0)
        layout.addWidget(bumpValueLe, 0, 1)
        layout.addWidget(QtGui.QLabel('Filter Type'), 1, 0)
        layout.addWidget(filterCbb, 1, 1)
        layout.addWidget(QtGui.QLabel('Alpha Is Lum'), 2, 0)
        layout.addWidget(ailCb, 2, 1)
        groupBox.setLayout(layout)
        # Connect
        bumpValueLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceBumpValueFloatOptVar',
                0, text))
        bumpValueLe.textEdited.connect(self._checkEmpty)
        filterCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit('shaderSpaceFilterTypeIntOptVar',
                0, str(idx)))
        ailCb.stateChanged.connect(
            lambda state: self.sender.emit(
                'shaderSpaceAlphaIsLuminanceIntOptVar',
                    0, str(state)))
        return groupBox

    def buildShaderComboBoxs(self):
        global gInitialOptions, kShadersList
        shader_index = gInitialOptions['shaderSpaceShaderIntOptVar']
        # Component
        shadersCbb = QtGui.QComboBox()
        shadersCbb.addItems(kShadersList)
        shadersCbb.setCurrentIndex(shader_index)
        shadersCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceShaderIntOptVar', 0, str(idx)))
        self.presetCbb = QtGui.QComboBox()
        self._resetPresets(kShadersList[shader_index])
        # Tip
        shadersCbb.setToolTip('Select a shader you want to create')
        self.presetCbb.setToolTip(
            'Select a preset you want to assign after create')
        # Layout
        groupBox = QtGui.QGroupBox('Shaders')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel('Shader Selections'), 0, 0)
        grid.addWidget(shadersCbb, 0, 1)
        grid.addWidget(QtGui.QLabel('Shader Presets'), 1, 0)
        grid.addWidget(self.presetCbb, 1, 1)
        groupBox.setLayout(grid)
        # Connect
        shadersCbb.activated[str].connect(
            lambda shaderType: self._resetPresets(shaderType))
        self.presetCbb.activated[str].connect(
            lambda preset: self._updatePreset(preset))
        # Component for up to Maya 2015
        if kMayaVersion in ('2015', '2016'):
            nameBuff = \
            gInitialOptions['shaderSpaceColorProfileNameStrOptVars']
            sRgbColorSpaceName = nameBuff[0]
            linearColorSpaceName = nameBuff[1]
            sRgbColorSpaceCbb = QtGui.QComboBox()
            linearColorSpaceCbb = QtGui.QComboBox()
            cmPrefs = mc.colorManagementPrefs(q=True, inputSpaceNames=True)
            sRgbColorSpaceCbb.addItems(cmPrefs)
            linearColorSpaceCbb.addItems(cmPrefs)
            idx = sRgbColorSpaceCbb.findText(
                sRgbColorSpaceName, QtCore.Qt.MatchFixedString)
            if idx >= 0:
                sRgbColorSpaceCbb.setCurrentIndex(idx)
            idx = linearColorSpaceCbb.findText(
                linearColorSpaceName, QtCore.Qt.MatchFixedString)
            if idx >= 0:
                linearColorSpaceCbb.setCurrentIndex(idx)
            # connect
            sRgbColorSpaceCbb.activated[str].connect(
                lambda name: self.sender.emit(
                    'shaderSpaceColorProfileNameStrOptVars', 0, name))
            linearColorSpaceCbb.activated[str].connect(
                lambda name: self.sender.emit(
                    'shaderSpaceColorProfileNameStrOptVars', 1, name))
            grid.addWidget(QtGui.QLabel('sRGB Color-Space'), 2, 0)
            grid.addWidget(sRgbColorSpaceCbb, 2, 1)
            grid.addWidget(QtGui.QLabel('Linear Color-Space'), 3, 0)
            grid.addWidget(linearColorSpaceCbb, 3, 1)
        return groupBox

    def buildExecuteButtons(self):
        # Widget
        self.createShaderButton = QtGui.QPushButton('Create')
        self.createShaderButton.setMinimumHeight(36)
        self.createShaderButton.setMinimumWidth(100)
        # Layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.createShaderButton)
        frame = QtGui.QFrame()
        frame.setLayout(layout)
        # Connect
        self.createShaderButton.clicked.connect(_shaderGenerate)
        return frame

    def _checkEmpty(self, context):
        if not context:
            self.createShaderButton.setEnabled(False)
        else:
            self.createShaderButton.setEnabled(True)

    def _updatePreset(self, preset):
        global gShaderPreset
        gShaderPreset = preset

    def _resetPresets(self, shaderType):
        self.presetCbb.clear()
        self.presetCbb.addItem('No Preset')
        search_dir = self._presetsDir+'/'+shaderType
        if not isdir(search_dir):
            return []
        presets_set = []
        for mel in listdir(search_dir):
            buff = splitext(mel)
            if buff[1] == '.mel':
                presets_set.append(buff[0])
        if presets_set:
            self.presetCbb.addItems(presets_set)

class ShaderSpaceToolsWin(QtGui.QWidget):
    sender = QtCore.Signal(str, int, str)
    uvsnapshot_ext_set = ('png', 'tif', 'jpg', 'tga', 'bmp')
    resolutions = ('512', '1024', '2048', '4096')
    uvsnapshot_col_set = ('Black', 'White', 'Red')
    uvsnapshot_col_map = ((0, 0, 0), (255, 255, 255), (255, 0, 0))
    export_poly_type = ('ma', 'mb', 'obj')
    selected_or_all = ('Selected', 'All')
    options_alignment = QtCore.Qt.AlignRight
    def __init__(self, parent=None):
        super(ShaderSpaceToolsWin, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.sender.connect(updateOptions)
        self.org_paths = copy.deepcopy(
            gInitialOptions['shaderSpaceToolsPathStrOptVars'])
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._uvSnapshotArea())
        layout.addWidget(self._exportPolygonsArea())
        layout.addWidget(self._photoshopFileCreateArea())
        layout.addWidget(self._shaderExportArea())
        self.setLayout(layout)

    def _uvSnapshotArea(self):
        global gInitialOptions
        options = copy.deepcopy(
            gInitialOptions['shaderSpaceUvSnapshotOptionIntOptVars'])
        # Group
        groupBox = QtGui.QGroupBox('Batch UV Snapshot')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        # Component
        uvssPathLe = QtGui.QLineEdit(self.org_paths[0])
        uvssPathLe.textChanged.connect(
            lambda text: self.sender.emit('shaderSpaceToolsPathStrOptVars',
                0, text))
        uvssBrowseBtn = QtGui.QPushButton('...')
        uvssBrowseBtn.setMinimumWidth(40)
        uvssExtCbb = QtGui.QComboBox()
        uvssExtCbb.addItems(self.uvsnapshot_ext_set)
        uvssExtCbb.setCurrentIndex(options[0])
        uvssResCbb = QtGui.QComboBox()
        uvssResCbb.addItems(self.resolutions)
        uvssResCbb.setCurrentIndex(options[1])
        uvssColorCbb = QtGui.QComboBox()
        uvssColorCbb.addItems(self.uvsnapshot_col_set)
        uvssColorCbb.setCurrentIndex(options[2])
        uvssSourceCbb = QtGui.QComboBox()
        uvssSourceCbb.addItems(('Visible Display Layers', 'Sets'))
        uvssSourceCbb.setCurrentIndex(options[3])
        uvssMakeBtn = QtGui.QPushButton('Snapshot')
        uvssMakeBtn.setMinimumWidth(80)
        # Layout
        right = QtCore.Qt.AlignRight
        vlayout = QtGui.QVBoxLayout()
        hlayout01 = QtGui.QHBoxLayout()
        hlayout02 = QtGui.QHBoxLayout()
        hlayout01.addWidget(QtGui.QLabel('Path'))
        hlayout01.addWidget(uvssPathLe)
        hlayout01.addWidget(uvssBrowseBtn)
        hlayout01.addWidget(uvssMakeBtn)
        hlayout02.addWidget(QtGui.QLabel('Extension'), 0, right)
        hlayout02.addWidget(uvssExtCbb, 0, right)
        hlayout02.addWidget(QtGui.QLabel('Resolutions'), 0, right)
        hlayout02.addWidget(uvssResCbb, 0, right)
        hlayout02.addWidget(QtGui.QLabel('Colors'), 0, right)
        hlayout02.addWidget(uvssColorCbb, 0, right)
        hlayout02.addWidget(QtGui.QLabel('Source'), 0, right)
        hlayout02.addWidget(uvssSourceCbb, 0, right)
        hlayout02.setAlignment(self.options_alignment)
        vlayout.addLayout(hlayout01)
        vlayout.addLayout(hlayout02)
        groupBox.setLayout(vlayout)
        # Connect
        uvssBrowseBtn.clicked.connect(
            partial(self._fileDialog, 'UV Snapshot Directory',
                uvssPathLe))
        uvssExtCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceUvSnapshotOptionIntOptVars', 0, str(idx)))
        uvssResCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceUvSnapshotOptionIntOptVars', 1, str(idx)))
        uvssColorCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceUvSnapshotOptionIntOptVars', 2, str(idx)))
        uvssSourceCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceUvSnapshotOptionIntOptVars', 3, str(idx)))
        uvssMakeBtn.clicked.connect(self._uv_snapshot)
        return groupBox

    def _exportPolygonsArea(self):
        global gInitialOptions
        options = gInitialOptions['shaderSpacePolygonExportOptionIntOptVars']
        includes= gInitialOptions['shaderSpacePolygonExportOptionStrOptVars']
        # Group
        groupBox = QtGui.QGroupBox('Batch Polygon Export')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        # Component
        pePathLe = QtGui.QLineEdit(self.org_paths[1])
        pePathBrowseBtn = QtGui.QPushButton('...')
        pePathBrowseBtn.setMinimumWidth(40)
        peModeCbb = QtGui.QComboBox()
        peModeCbb.addItems(('Maya Ascii', 'Maya Binary', 'Obj'))
        peModeCbb.setCurrentIndex(options[0])
        peSourceCbb = QtGui.QComboBox()
        peSourceCbb.addItems(('Visible Display Layers', 'Sets'))
        peModeCbb.setCurrentIndex(options[1])
        peExludeLe = QtGui.QLineEdit(includes[0])
        peIncludeLe = QtGui.QLineEdit(includes[1])
        peMakeBtn = QtGui.QPushButton('Export')
        peMakeBtn.setMinimumWidth(80)
        # Layout
        right = QtCore.Qt.AlignRight
        vlayout = QtGui.QVBoxLayout()
        hlayout01 = QtGui.QHBoxLayout()
        hlayout02 = QtGui.QHBoxLayout()
        hlayout01.addWidget(QtGui.QLabel('Path'))
        hlayout01.addWidget(pePathLe)
        hlayout01.addWidget(pePathBrowseBtn)
        hlayout01.addWidget(peMakeBtn)
        hlayout02.addWidget(QtGui.QLabel('Mode'))
        hlayout02.addWidget(peModeCbb)
        hlayout02.addWidget(QtGui.QLabel('Source'))
        hlayout02.addWidget(peSourceCbb)
        hlayout02.addWidget(QtGui.QLabel('Exclude'))
        hlayout02.addWidget(peExludeLe)
        hlayout02.addWidget(QtGui.QLabel('Include'))
        hlayout02.addWidget(peIncludeLe)
        hlayout02.setAlignment(self.options_alignment)
        vlayout.addLayout(hlayout01)
        vlayout.addLayout(hlayout02)
        groupBox.setLayout(vlayout)
        # Connect
        pePathLe.textChanged.connect(
            lambda text: self.sender.emit('shaderSpaceToolsPathStrOptVars',
                1, text))
        pePathBrowseBtn.clicked.connect(
            partial(self._fileDialog, 'Polygon Export Directory',
                pePathLe))
        peModeCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpacePolygonExportOptionIntOptVars', 0, str(idx)))
        peSourceCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpacePolygonExportOptionIntOptVars', 1, str(idx)))
        peExludeLe.textEdited.connect(
            lambda text: self.sender.emit(
                'shaderSpacePolygonExportOptionStrOptVars', 0, text))
        peIncludeLe.textEdited.connect(
            lambda text: self.sender.emit(
                'shaderSpacePolygonExportOptionStrOptVars', 1, text))
        peMakeBtn.clicked.connect(self._export_polygons)
        return groupBox

    def _photoshopFileCreateArea(self):
        # Group
        groupBox = QtGui.QGroupBox('Photoshop File Generate')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        # Component
        psPathLe = QtGui.QLineEdit(self.org_paths[2])
        psPathBrowseBtn = QtGui.QPushButton('...')
        psPathBrowseBtn.setMinimumWidth(40)
        psUvPathBrowseBtn = QtGui.QPushButton('...')
        psUvPathBrowseBtn.setMinimumWidth(40)
        psResCbb = QtGui.QComboBox()
        psResCbb.addItems(self.resolutions)
        psResCbb.setCurrentIndex(
            gInitialOptions['shaderSpacePhotoshopOptionIntOptVars'][0])
        psUvPathLe = QtGui.QLineEdit(self.org_paths[4])
        psNamesLe = QtGui.QLineEdit(
            gInitialOptions['shaderSpacePhotoshopNamesStrOptVars'][0])
        psUvLe = QtGui.QLineEdit(
            gInitialOptions['shaderSpacePhotoshopNamesStrOptVars'][1])
        psMakeBtn = QtGui.QPushButton('Generate')
        psMakeBtn.setMinimumWidth(80)
        # Conditions
        psNamesLe.setValidator(gLegalWindowFileName)
        psUvLe.setValidator(gLegalWindowFileName)
        # Layout
        vlayout = QtGui.QVBoxLayout()
        hlayout01 = QtGui.QHBoxLayout()
        hlayout02 = QtGui.QHBoxLayout()
        hlayout03 = QtGui.QHBoxLayout()
        hlayout01.addWidget(QtGui.QLabel('Path'))
        hlayout01.addWidget(psPathLe)
        hlayout01.addWidget(psPathBrowseBtn)
        hlayout01.addWidget(psMakeBtn)
        hlayout02.addWidget(QtGui.QLabel('UV Path'))
        hlayout02.addWidget(psUvPathLe)
        hlayout02.addWidget(psUvPathBrowseBtn)
        hlayout02.addWidget(QtGui.QLabel('Resolutions'))
        hlayout02.addWidget(psResCbb)
        hlayout02.setAlignment(self.options_alignment)
        hlayout03.addWidget(QtGui.QLabel('PS Names'))
        hlayout03.addWidget(psNamesLe)
        hlayout03.addWidget(QtGui.QLabel('UV Names'))
        hlayout03.addWidget(psUvLe)
        hlayout03.setAlignment(self.options_alignment)
        vlayout.addLayout(hlayout01)
        vlayout.addLayout(hlayout02)
        vlayout.addLayout(hlayout03)
        groupBox.setLayout(vlayout)
        # Connect
        psPathLe.textChanged.connect(
            lambda text: self.sender.emit(
                'shaderSpaceToolsPathStrOptVars', 2, text))
        psUvPathLe.textChanged.connect(
            lambda text: self.sender.emit(
                'shaderSpaceToolsPathStrOptVars', 4, text))
        psNamesLe.textChanged.connect(
            lambda text: self.sender.emit(
                'shaderSpacePhotoshopNamesStrOptVars', 0, text))
        psUvLe.textChanged.connect(
            lambda text: self.sender.emit(
                'shaderSpacePhotoshopNamesStrOptVars', 1, text))
        psPathBrowseBtn.clicked.connect(
            partial(self._fileDialog, 'Photoshop File Generate Directory',
                psPathLe))
        psUvPathBrowseBtn.clicked.connect(
            partial(self._fileDialog, 'UV Image Directory',
                psUvPathLe))
        psResCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpacePhotoshopOptionIntOptVars', 0, str(idx)))
        psMakeBtn.clicked.connect(self._photoshop_file_create)
        return groupBox

    def _shaderExportArea(self):
        global gInitialOptions
        # Group
        groupBox = QtGui.QGroupBox('Shader Export')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        # Component
        sePathLe = QtGui.QLineEdit(self.org_paths[3])
        sePathBrowseBtn = QtGui.QPushButton('...')
        sePathBrowseBtn.setMinimumWidth(40)
        seMakeBtn = QtGui.QPushButton('Export')
        seMakeBtn.setMinimumWidth(80)
        seMethodCbb = QtGui.QComboBox()
        seMethodCbb.addItems((self.selected_or_all))
        seMethodCbb.setCurrentIndex(
            gInitialOptions['shaderSpaceShaderExportIntOptVars'][0])
        # Layout
        vlayout = QtGui.QVBoxLayout()
        hlayout01 = QtGui.QHBoxLayout()
        hlayout02 = QtGui.QHBoxLayout()
        hlayout01.addWidget(QtGui.QLabel('Path'))
        hlayout01.addWidget(sePathLe)
        hlayout01.addWidget(sePathBrowseBtn)
        hlayout01.addWidget(seMakeBtn)
        hlayout02.addWidget(QtGui.QLabel('Method'))
        hlayout02.addWidget(seMethodCbb)
        hlayout02.setAlignment(QtCore.Qt.AlignLeft)
        hlayout02.setAlignment(self.options_alignment)
        vlayout.addLayout(hlayout01)
        vlayout.addLayout(hlayout02)
        groupBox.setLayout(vlayout)
        # Connect
        sePathLe.textChanged.connect(
            lambda text: self.sender.emit(
                'shaderSpaceToolsPathStrOptVars', 3, text))
        sePathBrowseBtn.clicked.connect(
            partial(self._fileDialog, 'Shader Export Directory',
                sePathLe))
        seMakeBtn.clicked.connect(self._export_shaders)
        seMethodCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceShaderExportIntOptVars', 0, str(idx)))
        return groupBox

    def _fileDialog(self, title, lineEdit):
        dir_name = QtGui.QFileDialog.getExistingDirectory(self,
            title, lineEdit.text())
        if dir_name:
            dir_name = dir_name.replace('\\', '/')
            lineEdit.setText(dir_name)

    def _uv_snapshot(self):
        options = gInitialOptions['shaderSpaceUvSnapshotOptionIntOptVars']
        save_path = gInitialOptions[
            'shaderSpaceToolsPathStrOptVars'][0].replace('\\', '/')
        ext = self.uvsnapshot_ext_set[options[0]]
        res = self.resolutions[options[1]]
        color = self.uvsnapshot_col_map[options[2]]
        uvSnapshot(save_path, ext, res, color, options[3])

    def _export_polygons(self):
        options = gInitialOptions['shaderSpacePolygonExportOptionIntOptVars']
        save_path = gInitialOptions[
            'shaderSpaceToolsPathStrOptVars'][1].replace('\\', '/')
        words = gInitialOptions['shaderSpacePolygonExportOptionStrOptVars']
        save_type = self.export_poly_type[options[0]]
        exportPolygons(save_path, save_type, words[0], words[1], options[1])

    def _photoshop_file_create(self):
        save_path = gInitialOptions[
            'shaderSpaceToolsPathStrOptVars'][2].replace('\\', '/')
        if save_path[-1] != '/':
            save_path = save_path + '/'
        obtain_uv_path = gInitialOptions[
            'shaderSpaceToolsPathStrOptVars'][4].replace('\\', '/')
        if obtain_uv_path and obtain_uv_path[-1] != '/':
            obtain_uv_path = obtain_uv_path + '/'
        check_channels = gInitialOptions['shaderSpaceChannelsIntOptVars']
        channel_abbrs = gInitialOptions['shaderSpaceAbbreviationsStrOptVars']
        resolution = self.resolutions[
            gInitialOptions['shaderSpacePhotoshopOptionIntOptVars'][0]]
        photoshop_names = gInitialOptions[
            'shaderSpacePhotoshopNamesStrOptVars'][0].split(',')
        uv_image_names = gInitialOptions[
            'shaderSpacePhotoshopNamesStrOptVars'][1].split(',')
        channels = [c for idx, c in enumerate(channel_abbrs)
            if check_channels[idx]]
        for index, name in enumerate(photoshop_names):
            uv_image = ''
            if index < len(uv_image_names):
                uv_image = obtain_uv_path + uv_image_names[index]
            if not name.endswith('.psd'):
                name = name + '.psd'
            createPhotoshopFile(save_path+name, uv_image, channels, resolution)

    def _export_shaders(self):
        save_path = gInitialOptions['shaderSpaceToolsPathStrOptVars'][3]
        method = self.selected_or_all[
            gInitialOptions['shaderSpaceShaderExportIntOptVars'][0]]
        exportShaders(save_path, method)

class ShaderSpaceSettingWin(QtGui.QWidget):
    sender = QtCore.Signal(str, int, str)
    def __init__(self, parent=None):
        super(ShaderSpaceSettingWin, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.sender.connect(updateOptions)
        layout = QtGui.QVBoxLayout()
        self.nodes = self._buildNodes()
        self.rules = self._buildRules()
        self.abbreviations = self._buildAbbreviations()
        layout.addWidget(self.nodes)
        layout.addWidget(self.rules)
        layout.addWidget(self.abbreviations)
        self.setLayout(layout)

    def _buildNodes(self):
        global gInitialOptions
        rules = copy.deepcopy(
            gInitialOptions['shaderSpaceNodeNameRuleStrOptVars'])
        # Component
        shaderLe = QtGui.QLineEdit(rules[0])
        sgLe = QtGui.QLineEdit(rules[1])
        texLe = QtGui.QLineEdit(rules[2])
        bmp2dLe = QtGui.QLineEdit(rules[3])
        p2dTexLe = QtGui.QLineEdit(rules[4])
        mtInfoLe = QtGui.QLineEdit(rules[5])
        # Layout
        groupBox = QtGui.QGroupBox('Maya Nodes')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel('texture'), 2, 0)
        layout.addWidget(QtGui.QLabel('shader'), 0, 0)
        layout.addWidget(shaderLe, 0, 1)
        layout.addWidget(QtGui.QLabel('shadingEngine'), 1, 0)
        layout.addWidget(sgLe, 1, 1)
        layout.addWidget(texLe, 2, 1)
        layout.addWidget(QtGui.QLabel('bump2d'), 3, 0)
        layout.addWidget(bmp2dLe, 3, 1)
        layout.addWidget(QtGui.QLabel('place2dTexture'), 4, 0)
        layout.addWidget(p2dTexLe, 4, 1)
        layout.addWidget(QtGui.QLabel('materialInfo'), 5, 0)
        layout.addWidget(mtInfoLe, 5, 1)
        self.setLayout(layout)
        groupBox.setToolTip('<asset> Asset Name\n<shader> Shader Name\
            \n<user> User Name\n<version> Version\
            \n<channel> Channel Abbreviations(texture and p2d only)')
        groupBox.setLayout(layout)
        # Connect
        shaderLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceNodeNameRuleStrOptVars',
                0, text))
        sgLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceNodeNameRuleStrOptVars',
                1, text))
        texLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceNodeNameRuleStrOptVars',
                2, text))
        bmp2dLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceNodeNameRuleStrOptVars',
                3, text))
        p2dTexLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceNodeNameRuleStrOptVars',
                4, text))
        mtInfoLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceNodeNameRuleStrOptVars',
                5, text))
        return groupBox

    def _buildRules(self):
        global gInitialOptions
        _buildRules = gInitialOptions['shaderSpaceAutoPathRuleStrOptVar']
        # Component
        texPathRuleLe = QtGui.QLineEdit(_buildRules)
        # Layout
        layout= QtGui.QHBoxLayout()
        layout.addWidget(QtGui.QLabel('Texture Path Rule'))
        layout.addWidget(texPathRuleLe)
        groupBox = QtGui.QGroupBox('Auto Texture Path')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        groupBox.setToolTip('<root> Project Path\n<asset> Asset Name\
            \n<shader> Shader Name\n<user> User Name\n<version> Version\
            \n<channel> Channel Abbreviations')
        groupBox.setLayout(layout)
        # Connect
        texPathRuleLe.textEdited.connect(
            lambda text: self.sender.emit('shaderSpaceAutoPathRuleStrOptVar',
                0, text))
        return groupBox

    def _buildAbbreviations(self):
        global kChannelList, gInitialOptions
        abbreviations = copy.deepcopy(
            gInitialOptions['shaderSpaceAbbreviationsStrOptVars'])
        group = QtGui.QGroupBox('Channel Abbreviations')
        group.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtGui.QGridLayout()
        self.abbreviations = []
        for col in range(4):
            for row in range(6):
                index = (col*3) + (row/2)
                if row % 2 == 0:
                    layout.addWidget(
                        QtGui.QLabel(kChannelList[index]), col, row)
                else:
                    field = QtGui.QLineEdit(abbreviations[index])
                    field.setValidator(gLegalMayaNodeName)
                    field.setMaximumWidth(80)
                    field.textEdited.connect(
                        lambda text, index=index: self.sender.emit(
                            'shaderSpaceAbbreviationsStrOptVars',
                                index, text))
                    layout.addWidget(field, col, row)
        group.setLayout(layout)
        return group

class AboutDialog(QtGui.QDialog):
    def __init__(self, parent=_getMayaMainWin()):
        super(AboutDialog, self).__init__(parent)
        self.setWindowTitle('Shader Space')
        self.initUI()

    def initUI(self):
        layout = QtGui.QVBoxLayout()
        contexts = ('Shader Space - Rapid build shader tool',
                    'Author : Chia Xin Lin',
                    'Version : '+kVersion,
                    'Last Update :'+kLastUpdate,
                    'E-Mail : nnnight@gmail.com',
                    'Github : http://github.com/chiaxin')
        for context in contexts:
            layout.addWidget(QtGui.QLabel(context))
        close_button = QtGui.QPushButton('OK')
        layout.addWidget(close_button)
        self.setLayout(layout)
        # Connect
        close_button.clicked.connect(self.close)

class HelpDialog(QtGui.QDialog):
    def __init__(self, parent=_getMayaMainWin()):
        super(HelpDialog, self).__init__(parent)
        self.setWindowTitle('Help')
        self.initUI()

    def initUI(self):
        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel('Help'))
        close_button = QtGui.QPushButton('OK')
        layout.addWidget(close_button)
        self.setLayout(layout)
        # Connect
        close_button.clicked.connect(self.close)

