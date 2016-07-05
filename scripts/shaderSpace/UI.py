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
from PySide import QtGui, QtCore
from shiboken import wrapInstance
from functools import partial
from math import ceil
import maya.cmds as mc
import maya.OpenMayaUI as omui
from config import *
from core import createShader

###############################################################
# User options dictionary
###############################################################
gInitialOptions = dict()
for optVar in kDefaultMappings.keys():
    if not mc.optionVar(exists=optVar):
        gInitialOptions[optVar] = copy.deepcopy(kDefaultMappings[optVar])
    else:
        gInitialOptions[optVar] = mc.optionVar(q=optVar)

###############################################################
# Validator
###############################################################
gValidMayaNode = QtGui.QRegExpValidator(
    QtCore.QRegExp(r'[a-zA-Z_]\w+'))

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
            gInitialOptions[optVar] = int(value)
        elif optVar.endswith('IntOptVars'):
            buff = gInitialOptions[optVar]
            buff[index] = int(value)
        elif optVar.endswith('FloatOptVar'):
            gInitialOptions[optVar] = float(value)
    except:
        raise

def getMayaMainWin():
    '''Get Maya main window using OpenMayaUI.MQtUtil'''
    pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(long(pointer), QtGui.QWidget)

def shaderGenerate():
    global gInitialOptions
    shader, shadingGroup = createShader(**gInitialOptions)
    print shader, shadingGroup

class ShaderSpaceMainWin(QtGui.QMainWindow):
    '''Shader Space Main Window'''
    def __init__(self, parent=getMayaMainWin()):
        super(ShaderSpaceMainWin, self).__init__(parent)
        self.setWindowTitle('Shader Space v'+kVersion)
        self.initUI()

    def initUI(self):
        centralWidget = ShaderSpaceCentral()
        self.setCentralWidget(centralWidget)
        self.statusBar()

    def closeEvent(self, event):
        self.storeOptionVars()
        event.accept()

    def storeOptionVars(self):
        global gInitialOptions
        from pymel.all import optionVar
        for var, value in gInitialOptions.items():
            optionVar[var] = value

class ShaderSpaceCentral(QtGui.QWidget):
    '''Main window central'''
    def __init__(self, parent=None):
        super(ShaderSpaceCentral, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # Widgets
        createWidget = ShaderSpaceCreateWin()
        toolsWidget = ShaderSpaceToolsWin()
        settingWidget = ShaderSpaceSettingWin()
        # Tab
        tab = QtGui.QTabWidget()
        tab.addTab(createWidget, 'Creation')
        tab.addTab(toolsWidget, 'Tools')
        tab.addTab(settingWidget, 'Settings')
        # Layouts
        layout = QtGui.QVBoxLayout()
        layout.addWidget(tab)
        self.setLayout(layout)

class ShaderSpaceCreateWin(QtGui.QWidget):
    '''Shader Space Creation Page'''
    # Signal object
    sender = QtCore.Signal(str, int, str)
    def __init__(self, parent=None):
        super(ShaderSpaceCreateWin, self).__init__(parent)
        self.initUI()

    def initUI(self):
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
        # Set validator
        assetLe.setValidator(gValidMayaNode)
        shaderLe.setValidator(gValidMayaNode)
        userLe.setValidator(gValidMayaNode)
        versionLe.setValidator(gValidMayaNode)
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
        return groupBox

    def buildChannelCheckBoxs(self):
        global kChannelList, gInitialOptions
        checks = copy.deepcopy(
            gInitialOptions['shaderSpaceChannelsIntOptVars'])
        numOfChannels = len(kChannelList)
        grid = QtGui.QGridLayout()
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
        afpCbb.addItem('Auto fill path')
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
        filter_index = gInitialOptions['shaderSpaceFilterTypeIntOptVar']
        bump_value = gInitialOptions['shaderSpaceBumpValueFloatOptVar']
        # Component
        bumpValueLe = QtGui.QLineEdit(str(bump_value))
        bumpValueLe.setMaximumWidth(60)
        bumpValueLe.setValidator(bvValidator)
        filterCbb = QtGui.QComboBox()
        filterCbb.addItems(
            ('off', 'Mipmap', 'Box', 'Quadratic', 'Quartic', 'Gaussian'))
        filterCbb.setCurrentIndex(filter_index)
        ailCb = QtGui.QCheckBox()
        ail_state = QtCore.Qt.CheckState.Unchecked
        if gInitialOptions['shaderSpaceAlphaIsLuminanceIntOptVar']:
            ail_state = QtCore.Qt.CheckState.Checked
        ailCb.setCheckState(ail_state)
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
        presetCbb = QtGui.QComboBox()
        presetCbb.addItem('No Preset')
        # Layout
        groupBox = QtGui.QGroupBox('Shaders')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel('Shader Selections'), 0, 0)
        grid.addWidget(shadersCbb, 0, 1)
        grid.addWidget(QtGui.QLabel('Shader Presets'), 1, 0)
        grid.addWidget(presetCbb, 1, 1)
        groupBox.setLayout(grid)
        return groupBox

    def buildExecuteButtons(self):
        # Widget
        createBtn = QtGui.QPushButton('Create')
        createBtn.setMinimumHeight(36)
        createBtn.setMinimumWidth(100)
        # Layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(createBtn)
        frame = QtGui.QFrame()
        frame.setLayout(layout)
        # Connect
        createBtn.clicked.connect(shaderGenerate)
        return frame

class ShaderSpaceToolsWin(QtGui.QWidget):
    sender = QtCore.Signal(str, int, str)
    def __init__(self, parent=None):
        super(ShaderSpaceToolsWin, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.sender.connect(updateOptions)
        self.org_paths = copy.deepcopy(
            gInitialOptions['shaderSpaceToolsPathStrOptVars'])
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.uvsnapshot())
        layout.addWidget(self.polygonExport())
        layout.addWidget(self.photoshopFileCreate())
        layout.addWidget(self.shaderExport())
        self.setLayout(layout)

    def uvsnapshot(self):
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
        uvssBrowseBtn = QtGui.QPushButton('browse')
        uvssBrowseBtn.setMaximumWidth(60)
        uvssExtCbb = QtGui.QComboBox()
        uvssExtCbb.addItems(('png', 'tif', 'jpg', 'tga', 'bmp'))
        uvssResCbb = QtGui.QComboBox()
        uvssResCbb.setCurrentIndex(options[0])
        uvssResCbb.addItems(('512', '1024', '2048', '4096'))
        uvssResCbb.setCurrentIndex(options[1])
        uvssColorCbb = QtGui.QComboBox()
        uvssColorCbb.addItems(('Black', 'White', 'Red'))
        uvssColorCbb.setCurrentIndex(options[2])
        uvssSourceCbb = QtGui.QComboBox()
        uvssSourceCbb.addItems(('Display Layer', 'Sets'))
        uvssSourceCbb.setCurrentIndex(options[3])
        uvssMakeBtn = QtGui.QPushButton('Snapshot')
        # Layout
        right = QtCore.Qt.AlignRight
        vlayout = QtGui.QVBoxLayout()
        hlayout01 = QtGui.QHBoxLayout()
        hlayout02 = QtGui.QHBoxLayout()
        hlayout01.addWidget(QtGui.QLabel('Path'))
        hlayout01.addWidget(uvssPathLe)
        hlayout01.addWidget(uvssBrowseBtn)
        hlayout01.addWidget(uvssMakeBtn)
        hlayout02.addWidget(QtGui.QLabel('Resolutions'), 0, right)
        hlayout02.addWidget(uvssResCbb, 0, right)
        hlayout02.addWidget(QtGui.QLabel('Colors'), 0, right)
        hlayout02.addWidget(uvssColorCbb, 0, right)
        hlayout02.addWidget(QtGui.QLabel('Source'), 0, right)
        hlayout02.addWidget(uvssSourceCbb, 0, right)
        vlayout.addLayout(hlayout01)
        vlayout.addLayout(hlayout02)
        groupBox.setLayout(vlayout)
        # Connect
        uvssBrowseBtn.clicked.connect(
            partial(self.fileDialog, 'UV Snapshot Directory',
                uvssPathLe))
        uvssResCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceUvSnapshotOptionIntOptVars', 0, str(idx)))
        uvssColorCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceUvSnapshotOptionIntOptVars', 1, str(idx)))
        uvssSourceCbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceUvSnapshotOptionIntOptVars', 2, str(idx)))
        return groupBox

    def polygonExport(self):
        global gInitialOptions
        options = gInitialOptions['shaderSpacePolygonExportOptionIntOptVars']
        includes= gInitialOptions['shaderSpacePolygonExportOptionStrOptVars']
        # Group
        groupBox = QtGui.QGroupBox('Batch Polygon Export')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        # Component
        pePathLe = QtGui.QLineEdit(self.org_paths[1])
        pePathLe.textChanged.connect(
            lambda text: self.sender.emit('shaderSpaceToolsPathStrOptVars',
                1, text))
        pePathBrowseBtn = QtGui.QPushButton('browse')
        pePathBrowseBtn.setMaximumWidth(60)
        peModeCbb = QtGui.QComboBox()
        peModeCbb.addItems(('Maya Ascii', 'Maya Binary', 'Obj'))
        peModeCbb.setCurrentIndex(options[0])
        peSourceCbb = QtGui.QComboBox()
        peSourceCbb.addItems(('Display Layer', 'Sets'))
        peModeCbb.setCurrentIndex(options[1])
        peExludeLe = QtGui.QLineEdit(includes[0])
        peIncludeLe = QtGui.QLineEdit(includes[1])
        self.peMakeBtn = QtGui.QPushButton('Export')
        # Layout
        right = QtCore.Qt.AlignRight
        vlayout = QtGui.QVBoxLayout()
        hlayout01 = QtGui.QHBoxLayout()
        hlayout02 = QtGui.QHBoxLayout()
        hlayout01.addWidget(QtGui.QLabel('Path'))
        hlayout01.addWidget(pePathLe)
        hlayout01.addWidget(pePathBrowseBtn)
        hlayout01.addWidget(self.peMakeBtn)
        hlayout02.addWidget(QtGui.QLabel('Mode'))
        hlayout02.addWidget(peModeCbb)
        hlayout02.addWidget(QtGui.QLabel('Source'))
        hlayout02.addWidget(peSourceCbb)
        hlayout02.addWidget(QtGui.QLabel('Exclude'))
        hlayout02.addWidget(peExludeLe)
        hlayout02.addWidget(QtGui.QLabel('Include'))
        hlayout02.addWidget(peIncludeLe)
        vlayout.addLayout(hlayout01)
        vlayout.addLayout(hlayout02)
        groupBox.setLayout(vlayout)
        # Connect
        pePathBrowseBtn.clicked.connect(
            partial(self.fileDialog, 'Polygon Export Directory',
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
        return groupBox

    def photoshopFileCreate(self):
        # Group
        groupBox = QtGui.QGroupBox('Photoshop File Generate')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        # Component
        psPathLe = QtGui.QLineEdit(self.org_paths[2])
        psPathBrowseBtn = QtGui.QPushButton('browse')
        psPathBrowseBtn.setMaximumWidth(60)
        psNamesLe = QtGui.QLineEdit()
        psUVsLe = QtGui.QLineEdit()
        psMakeBtn = QtGui.QPushButton('Generate')
        # Layout
        vlayout = QtGui.QVBoxLayout()
        hlayout01 = QtGui.QHBoxLayout()
        hlayout02 = QtGui.QHBoxLayout()
        hlayout01.addWidget(QtGui.QLabel('Path'))
        hlayout01.addWidget(psPathLe)
        hlayout01.addWidget(psPathBrowseBtn)
        hlayout01.addWidget(psMakeBtn)
        hlayout02.addWidget(QtGui.QLabel('PS Names'))
        hlayout02.addWidget(psNamesLe)
        hlayout02.addWidget(QtGui.QLabel('UV Names'))
        hlayout02.addWidget(psUVsLe)
        vlayout.addLayout(hlayout01)
        vlayout.addLayout(hlayout02)
        groupBox.setLayout(vlayout)
        # Connect
        psPathLe.textChanged.connect(
            lambda text: self.sender.emit(
                'shaderSpaceToolsPathStrOptVars', 2, text))
        psPathBrowseBtn.clicked.connect(
            partial(self.fileDialog, 'Photoshop File Generate Directory',
                psPathLe))
        return groupBox

    def shaderExport(self):
        global gInitialOptions
        # Group
        groupBox = QtGui.QGroupBox('Shader Export')
        groupBox.setAlignment(QtCore.Qt.AlignCenter)
        # Component
        sePathLe = QtGui.QLineEdit(self.org_paths[3])
        sePathBrowseBtn = QtGui.QPushButton('browse')
        sePathBrowseBtn.setMaximumWidth(60)
        seMakeBtn = QtGui.QPushButton('Export')
        seMethodCbb = QtGui.QComboBox()
        for method in ('Selected', 'All'):
            seMethodCbb.addItem(method)
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
        vlayout.addLayout(hlayout01)
        vlayout.addLayout(hlayout02)
        groupBox.setLayout(vlayout)
        # Connect
        sePathLe.textChanged.connect(
            lambda text: self.sender.emit(
                'shaderSpaceToolsPathStrOptVars', 3, text))
        sePathBrowseBtn.clicked.connect(
            partial(self.fileDialog, 'Shader Export Directory',
                sePathLe))
        return groupBox

    def fileDialog(self, title, lineEdit):
        dir_name = QtGui.QFileDialog.getExistingDirectory(self,
            title, lineEdit.text())
        if dir_name:
            dir_name = dir_name.replace('\\', '/')
            lineEdit.setText(dir_name)

class ShaderSpaceSettingWin(QtGui.QWidget):
    sender = QtCore.Signal(str, int, str)
    vaildNode = QtCore.QRegExp(
        '\\D(<asset>|<shader>|<user>|<version>|<channel>|\\w)*')
    vaildNodeWithoutChannel = QtCore.QRegExp(
        '\\D(<asset>|<shader>|<user>|<version>|\\w)*')
    def __init__(self, parent=None):
        super(ShaderSpaceSettingWin, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.sender.connect(updateOptions)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.nodes())
        layout.addWidget(self.rule())
        layout.addWidget(self.abbreviation())
        self.setLayout(layout)

    def nodes(self):
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
            \n<channel> Channel Abbreviations')
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

    def rule(self):
        global gInitialOptions
        rule = gInitialOptions['shaderSpaceAutoPathRuleStrOptVar']
        # Component
        texPathRuleLe = QtGui.QLineEdit(rule)
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

    def abbreviation(self):
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
                    field.setValidator(gValidMayaNode)
                    field.setMaximumWidth(80)
                    field.textEdited.connect(
                        lambda text, index=index: self.sender.emit(
                            'shaderSpaceAbbreviationsStrOptVars',
                                index, text))
                    layout.addWidget(field, col, row)
        group.setLayout(layout)
        return group
