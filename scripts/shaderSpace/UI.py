# -*- coding: utf-8 -*-
# shaderSpace main user interface
#
# Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
#
# E-Mail : nnnight@gmail.com
#
# Github : http://github.com/chiaxin
#
# Licensed under MIT: https://opensource.org/licenses/MIT
#
# Python modules
from os import listdir
from os.path import isfile, isdir, splitext, basename
import copy
import pickle
from functools import partial
from math import ceil
# PySide modules
from PySide import QtGui, QtCore
from shiboken import wrapInstance
# Maya
import maya.cmds as mc
import maya.mel as mel
import maya.OpenMayaUI as omui
# shaderSpace modules
import tools
import ilrocc
from config import *
from core import createShader
from deswatches import SwatchesDegammaWin

# UI Common
_LINE_EDIT_HEIGHT = 24

# User options dict
_PRESERVE = dict()
for key in kDefaultMappings.keys():
    if mc.optionVar(ex=key):
        _PRESERVE[key] = mc.optionVar(q=key)
    else:
        _PRESERVE[key] = copy.deepcopy(kDefaultMappings[key])
_SHADER_PRESET = 'No Preset'
_VAILD_MAYA_NODE_NAME = QtGui.QRegExpValidator(QtCore.QRegExp(r'\w+'))
_VAILD_WIN_FILE_NAME = QtGui.QRegExpValidator(
    QtCore.QRegExp('^[^\/\\\:\*\?\"\<\>\| ]+$'))

# Custom slot
@QtCore.Slot(str, int, str)
def _updateOptionVarsSlot(optVar, index, value):
    global _PRESERVE
    if not _PRESERVE.has_key(optVar):
        print '<shaderSpace> That is have no option key:{0}'.format(optVar)
        return
    try:
        if optVar.endswith('StrOptVars'):
            buff = _PRESERVE[optVar]
            buff[index] = value
        elif optVar.endswith('StrOptVar'):
            _PRESERVE[optVar] = value
        elif optVar.endswith('IntOptVar'):
            if value in ('True', 'False'):
                _PRESERVE[optVar] = int(value == 'True')
            else:
                _PRESERVE[optVar] = int(value)
        elif optVar.endswith('IntOptVars'):
            buff = _PRESERVE[optVar]
            buff[index] = int(value)
        elif optVar.endswith('FloatOptVar'):
            if value:
                _PRESERVE[optVar] = float(value)
        else:
            print '# Failed when save option'
    except:
        print '<shaderSpace> Write options var failed in {0}'.format(optVar)
        raise

def _saveOptionVarsIntoMaya():
    for key, item in _PRESERVE.items():
        if isinstance(item, basestring):
            mc.optionVar(sv=(key, str(item)))
        elif isinstance(item, int):
            mc.optionVar(iv=(key, int(item)))
        elif isinstance(item, float):
            mc.optionVar(fv=(key, float(item)))
        elif isinstance(item, (list, tuple)):
            mc.optionVar(remove=key)
            if isinstance(item[0], basestring):
                mc.optionVar(sv=(key, item[0]))
                for elem in item[1:]:
                    mc.optionVar(sva=(key, elem))
            elif isinstance(item[0], int):
                mc.optionVar(iv=(key, item[0]))
                for elem in item[1:]:
                    mc.optionVar(iva=(key, elem))
            elif isinstance(item[0], float):
                mc.optionVar(fv=(key, item[0]))
                for elem in item[1:]:
                    mc.optionVar(fva=(key, elem))
        else:
            print '# Unknown type : ', type(value)
            return False
    return True

def _getMayaMainWin():
    pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(long(pointer), QtGui.QWidget)

def _createShader():
    global _PRESERVE, _SHADER_PRESET
    shader = kShadersList[_PRESERVE['shaderSpaceShaderIntOptVar']]
    confirm = QtGui.QMessageBox()
    confirm.setWindowTitle('Create Shader Confirm')
    confirm.setText('<h3>Create {0} Shader.</h3>'.format(shader))
    confirm.setInformativeText('Do you want to create?')
    confirm.setStandardButtons(
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
    confirm.setDefaultButton(QtGui.QMessageBox.Cancel)
    ret = confirm.exec_()
    if ret == QtGui.QMessageBox.Cancel:
        return ''
    # - 
    shader, shadingGroup = createShader(preset=_SHADER_PRESET, **_PRESERVE)
    if shader:
        print shader, shadingGroup, ' has been created.'

def _folderDialog(lineEdit, title='File Dialog', parent=None):
    if not lineEdit.text():
        default_dir = mc.workspace(q=True, rd=True)
    else:
        default_dir = lineEdit.text()
    dir_name = QtGui.QFileDialog.getExistingDirectory(
        parent, title, default_dir)
    if dir_name:
        dir_name = dir_name.replace('\\', '/')
        lineEdit.setText(dir_name)

def _saveFileDialog(lineEdit, 
                    file_filter='',
                    sel_filter='',
                    title='Save File', 
                    parent=None):
    file_name = QtGui.QFileDialog.getSaveFileName(
        parent, title, mc.workspace(q=True, rd=True), file_filter, sel_filter)
    if file_name:
        lineEdit.setText(file_name[0])

def _openFileDialog(lineEdit,
                    file_filter='',
                    sel_filter='',
                    title='Open File',
                    parent=None):
    file_name = QtGui.QFileDialog.getOpenFileName(
        parent, title, mc.workspace(q=True, rd=True), file_filter, sel_filter)
    if file_name:
        lineEdit.setText(file_name[0])

def _findIconImage(icon_name):
    for path in mel.eval('getenv XBMLANGPATH').split(';'):
        if isfile(path + '/' + icon_name):
            return path + '/' + icon_name
    return ''

class ShaderSpaceMainWin(QtGui.QMainWindow):
    '''Shader Space Main Window'''
    sender = QtCore.Signal(str, int, str)
    OBJECT_NAME = 'shaderSpaceMainWin'
    def __init__(self, parent=_getMayaMainWin()):
        super(ShaderSpaceMainWin, self).__init__(parent)
        self.sender.connect(_updateOptionVarsSlot)
        self.setObjectName(self.OBJECT_NAME)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Shader Space v'+kVersion)
        icon = _findIconImage('shaderSpace.png')
        if icon: self.setWindowIcon(QtGui.QIcon(icon))
        # Initial
        self.centralWin = ShaderSpaceCentral()
        self.setCentralWidget(self.centralWin)
        self.resize(self.minimumSizeHint())
        self.toolbars()

    def toolbars(self):
        self.save_act   = QtGui.QAction(QtGui.QIcon(
            _findIconImage('shaderSpaceSave.png')), 'Save Settings', self)
        self.load_act   = QtGui.QAction(QtGui.QIcon(
            _findIconImage('shaderSpaceLoad.png')), 'Load Settings', self)
        self.reset_act  = QtGui.QAction(QtGui.QIcon(
            _findIconImage('shaderSpaceReset.png')), 'Reset Settings', self)
        self.lock_act   = QtGui.QAction(QtGui.QIcon(
            _findIconImage('shaderSpaceLock.png')), 'Lock Settings',
                self, checkable=True)
        self.deg_act    = QtGui.QAction(QtGui.QIcon(
            _findIconImage('shaderSpaceDegamma.png')), 'Degamma Swatches', self)
        self.expall_act = QtGui.QAction(QtGui.QIcon(
            _findIconImage('shaderSpaceExportAll.png')), 
                'Export All Shaders', self)
        self.expsel_act = QtGui.QAction(QtGui.QIcon(
            _findIconImage('shaderSpaceExportSel.png')), 
                'Export Selected Shaders', self)
        self.help_act   = QtGui.QAction(QtGui.QIcon(
            _findIconImage('shaderSpaceHelp.png')), 'Help', 
                self, checkable=True)
        # File toolbar
        self.file_toolbar = self.addToolBar('File')
        self.file_toolbar.setFloatable(False)
        self.file_toolbar.setMovable(False)
        self.file_toolbar.setIconSize(QtCore.QSize(32, 32))
        self.file_toolbar.addAction(self.save_act)
        self.file_toolbar.addAction(self.load_act)
        self.file_toolbar.addAction(self.reset_act)
        self.file_toolbar.addAction(self.lock_act)
        # Edit toolbar
        self.edit_toolbar = self.addToolBar('Edit')
        self.edit_toolbar.setFloatable(False)
        self.edit_toolbar.setMovable(False)
        self.edit_toolbar.setIconSize(QtCore.QSize(32, 32))
        self.edit_toolbar.addAction(self.deg_act)
        self.edit_toolbar.addAction(self.expall_act)
        self.edit_toolbar.addAction(self.expsel_act)
        # Help toolbar
        self.help_toolbar = self.addToolBar('Help')
        self.help_toolbar.setFloatable(False)
        self.help_toolbar.setMovable(False)
        self.help_toolbar.setIconSize(QtCore.QSize(32, 32))
        self.help_toolbar.addAction(self.help_act)
        # Connect
        self.save_act.triggered.connect(self._dumpSave)
        self.load_act.triggered.connect(self._dumpLoad)
        self.reset_act.triggered.connect(self._resetSettings)
        self.deg_act.triggered.connect(self.showSwatchesDegammaWin)
        self.lock_act.toggled.connect(self._lockSettings)
        self.lock_act.toggled.connect(lambda state: self.sender.emit(
            'shaderSpaceSettingsLockedIntOptVar', 0, str(state)))
        self.expall_act.triggered.connect(partial(self._do_export_shaders, 0))
        self.expsel_act.triggered.connect(partial(self._do_export_shaders, 1))
        self.help_act.triggered[bool].connect(self.centralWin.goToHelpPage)
        #
        self.lock_act.setChecked(
            bool(_PRESERVE['shaderSpaceSettingsLockedIntOptVar']))

    def closeEvent(self, event):
        if _saveOptionVarsIntoMaya():
            print '# Save option var successiful'
        else:
            print '# Save option var failed'
        event.accept()

    def showSwatchesDegammaWin(self):
        if not mc.ls(sl=True):
            print '# Please select one object!'
            return
        swatchesDegammaWin = SwatchesDegammaWin(self)
        swatchesDegammaWin.show()

    def _lockSettings(self, triggered):
        settingsWidget = self.centralWin.main_tw.widget(1)
        if triggered:
            settingsWidget.setEnabled(False)
        else:
            settingsWidget.setEnabled(True)

    def _resetSettings(self):
        msgbox = QtGui.QMessageBox()
        msgbox.setWindowTitle('Reset')
        msgbox.setText('<h3>The settings has been reset.</h3>')
        msgbox.setInformativeText('Do you want to reset?')
        msgbox.setStandardButtons(
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        msgbox.setDefaultButton(QtGui.QMessageBox.Cancel)
        ret = msgbox.exec_()
        if ret == QtGui.QMessageBox.Cancel:
            return
        _PRESERVE['shaderSpaceNodeNameRuleStrOptVars'] = \
            copy.deepcopy(
                kDefaultMappings['shaderSpaceNodeNameRuleStrOptVars'])
        _PRESERVE['shaderSpaceAutoPathRuleStrOptVar'] = \
            copy.deepcopy(
                kDefaultMappings['shaderSpaceAutoPathRuleStrOptVar'])
        _PRESERVE['shaderSpaceAbbreviationsStrOptVars'] = \
            copy.deepcopy(
                kDefaultMappings['shaderSpaceAbbreviationsStrOptVars'])
        self._reloadWidget(1)

    def _reloadWidget(self, idx):
        is_enabled = self.centralWin.main_tw.widget(idx).isEnabled()
        self.centralWin.resetSettingWidget()
        self.centralWin.main_tw.widget(idx).setEnabled(is_enabled)

    def _dumpSave(self):
        global _PRESERVE
        data_file, fl = QtGui.QFileDialog.getSaveFileName(
            self, 'Save settings',
            mc.workspace(q=True, rootDirectory=True), 'spk (*.spk)')
        if not data_file:
            return
        dumpDataSet = []
        dumpDataSet.append(_PRESERVE['shaderSpaceNodeNameRuleStrOptVars'])
        dumpDataSet.append(_PRESERVE['shaderSpaceAutoPathRuleStrOptVar'])
        dumpDataSet.append(_PRESERVE['shaderSpaceAbbreviationsStrOptVars'])
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
        global _PRESERVE
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
            _PRESERVE['shaderSpaceNodeNameRuleStrOptVars'] = nodeNameRuleBuff
            _PRESERVE['shaderSpaceAutoPathRuleStrOptVar'] = autoPathRuleBuff
            _PRESERVE['shaderSpaceAbbreviationsStrOptVars'] = abbreviationsBuff
            self._reloadWidget(1)
        finally:
            io_file.close()

    # 0: all, 1: selected
    def _do_export_shaders(self, source=0):
        export_dir = QtGui.QFileDialog.getExistingDirectory(
            self, "Export Shader Directory", mc.workspace(q=True, dir=True))
        if export_dir:
            export_dir.replace('\\', '/')
            if not export_dir.endswith('/'):
                export_dir = export_dir + '/'
            tools.exportShaders(export_dir, source)

class ShaderSpaceCentral(QtGui.QWidget):
    '''Main window central'''
    def __init__(self, parent=None):
        super(ShaderSpaceCentral, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.main_vl        = QtGui.QVBoxLayout()
        self.main_sw        = QtGui.QStackedWidget()
        self.main_tw        = QtGui.QTabWidget()
        #
        self.main_vl.addWidget(self.main_sw)
        #
        self.main_sw.addWidget(self.main_tw)
        self.main_sw.addWidget(self.helpWin())
        # Widgets
        self.createWidget   = ShaderSpaceCreateWin()
        self.settingWidget  = ShaderSpaceSettingWin()
        self.uvsWidget      = ShaderSpaceUVsWin()
        self.psdWidget      = ShaderSpacePsdWin()
        self.meshExpWidget  = ShaderSpaceMeshExportWin()
        self.bakerWidget    = ShaderSpaceBakerWin()
        # Main table layout
        self.main_tw.addTab(self.createWidget,  'Creation')
        self.main_tw.addTab(self.settingWidget, 'Settings')
        self.main_tw.addTab(self.uvsWidget,     'UV Snapshot')
        self.main_tw.addTab(self.psdWidget,     'Photoshop')
        self.main_tw.addTab(self.meshExpWidget, 'Mesh Export')
        self.main_tw.addTab(self.bakerWidget,   'Baker')
        # Set layout
        self.setLayout(self.main_vl)

    def helpWin(self):
        self.main_help_win  = QtGui.QWidget()
        self.help_vl        = QtGui.QVBoxLayout()
        self.help_tw        = QtGui.QTabWidget()
        self.help_vl.addWidget(self.help_tw)
        self.help_tw.addTab(self.helpPage(), 'Help')
        self.help_tw.addTab(self.aboutPage(), 'About')
        self.main_help_win.setLayout(self.help_vl)
        return self.main_help_win

    def helpPage(self):
        self.helpWin = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        for line in kHelpInfo:
            layout.addWidget(QtGui.QLabel('<h3>' + line + '</h3>'))
        self.helpWin.setLayout(layout)
        return self.helpWin

    def aboutPage(self):
        self.aboutWin = QtGui.QWidget()
        self.about_te = QtGui.QTextEdit()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.about_te)
        for l in kAboutInfo: self.about_te.append(l)
        self.about_te.setReadOnly(True)
        self.aboutWin.setLayout(layout)
        return self.aboutWin

    def resetSettingWidget(self):
        self.main_tw.removeTab(1)
        self.settingWidget.deleteLater()
        self.settingWidget = ShaderSpaceSettingWin()
        self.main_tw.insertTab(1, self.settingWidget, 'Settings')
        self.main_tw.setCurrentIndex(1)

    def goToHelpPage(self, state=False):
        if state:
            self.main_sw.setCurrentIndex(1)
        else:
            self.main_sw.setCurrentIndex(0)

class ShaderSpaceCreateWin(QtGui.QWidget):
    '''Shader Space Creation Page'''
    sender = QtCore.Signal(str, int, str)
    global _PRESERVE
    global _VAILD_MAYA_NODE_NAME
    global kChannelList
    global kShadersList
    global _SHADER_PRESET
    # Signal object
    _presetsDir = mc.internalVar(ups=True)+'attrPresets/'
    def __init__(self, parent=None):
        super(ShaderSpaceCreateWin, self).__init__(parent)
        self.sender.connect(_updateOptionVarsSlot)
        self.initUI()

    def initUI(self):
        # self.sender.connect(_updateOptionVarsSlot)
        self.main_gl = QtGui.QGridLayout()
        self.main_gl.addWidget(self._nameingField(), 0, 0)
        self.main_gl.addWidget(self._optionsField(), 0, 1)
        self.main_gl.addWidget(self._channelsField(), 1, 0)
        self.main_gl.addWidget(self._vauleField(), 1, 1)
        self.main_gl.addWidget(self._shadersField(), 2, 0)
        self.main_gl.addWidget(self._executeField(), 2, 1)
        self.setLayout(self.main_gl)

    def _nameingField(self):
        names = copy.deepcopy(_PRESERVE['shaderSpaceNameStrOptVars'])
        self.asset_le   = QtGui.QLineEdit(names[0])
        self.shader_le  = QtGui.QLineEdit(names[1])
        self.user_le    = QtGui.QLineEdit(names[2])
        self.version_le = QtGui.QLineEdit(names[3])
        self.name_fl = QtGui.QFormLayout()
        self.name_fl.setHorizontalSpacing(10)
        self.name_fl.addRow('Asset',    self.asset_le)
        self.name_fl.addRow('Shader',   self.shader_le)
        self.name_fl.addRow('User',     self.user_le)
        self.name_fl.addRow('Version',  self.version_le)
        self.name_gb = QtGui.QGroupBox('Name')
        self.name_gb.setAlignment(QtCore.Qt.AlignCenter)
        self.name_gb.setLayout(self.name_fl)
        self.asset_le.textEdited.connect(
            lambda t: self.sender.emit('shaderSpaceNameStrOptVars', 0, str(t)))
        self.shader_le.textEdited.connect(
            lambda t: self.sender.emit('shaderSpaceNameStrOptVars', 1, str(t)))
        self.user_le.textEdited.connect(
            lambda t: self.sender.emit('shaderSpaceNameStrOptVars', 2, str(t)))
        self.version_le.textEdited.connect(
            lambda t: self.sender.emit('shaderSpaceNameStrOptVars', 3, str(t)))
        for idx in range(self.name_fl.count()):
            widget = self.name_fl.itemAt(idx).widget()
            if isinstance(widget, QtGui.QLineEdit):
                widget.setValidator(_VAILD_MAYA_NODE_NAME)
                widget.setMinimumHeight(24)
                widget.setMaximumWidth(180)
                widget.textEdited.connect(self._checkEmpty)
        return self.name_gb

    def _channelsField(self):
        checks = copy.deepcopy(_PRESERVE['shaderSpaceChannelsIntOptVars'])
        self.channel_gl = QtGui.QGridLayout()
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
                self.channel_gl.addWidget(checkBox, col, row)
        self.channel_gb = QtGui.QGroupBox('Channels')
        self.channel_gb.setAlignment(QtCore.Qt.AlignCenter)
        self.channel_gb.setLayout(self.channel_gl)
        return self.channel_gb

    def _optionsField(self):
        options = copy.deepcopy(_PRESERVE['shaderSpaceOptionIntOptVars'])
        self.channel_vl = QtGui.QVBoxLayout()
        # Component
        self.assign_cbb = QtGui.QComboBox()
        self.assign_cbb.addItems(('No Assign Selected', 'Assign Selected'))
        self.assign_cbb.setCurrentIndex(options[0])
        self.gc_cbb = QtGui.QComboBox()
        self.muv_cbb = QtGui.QComboBox()
        self.afp_cbb = QtGui.QComboBox()
        self.sp2d_cbb = QtGui.QComboBox()
        self.gc_cbb.addItems(('No Gamma Correct', 'Gamma Correct'))
        self.afp_cbb.addItems(('Auto fill texture', 
            'Auto fill only exists', 'No auto fill texture'))
        self.muv_cbb.addItems(
            ('No Mirror', 'Mirror U', 'Mirror V', 'Mirror both'))
        self.sp2d_cbb.addItems(('Share place2dTexture', 'No share'))
        self.gc_cbb.setCurrentIndex(options[1])
        self.afp_cbb.setCurrentIndex(options[2])
        self.muv_cbb.setCurrentIndex(options[3])
        self.sp2d_cbb.setCurrentIndex(options[4])
        # Add
        self.channel_vl.addWidget(self.assign_cbb)
        self.channel_vl.addWidget(self.gc_cbb)
        self.channel_vl.addWidget(self.afp_cbb)
        self.channel_vl.addWidget(self.muv_cbb)
        self.channel_vl.addWidget(self.sp2d_cbb)
        # Connect
        self.assign_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit('shaderSpaceOptionIntOptVars', 0, 
                str(idx)))
        self.gc_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit('shaderSpaceOptionIntOptVars', 1, 
                str(idx)))
        self.afp_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit('shaderSpaceOptionIntOptVars', 2, 
                str(idx)))
        self.muv_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit('shaderSpaceOptionIntOptVars', 3, 
                str(idx)))
        self.sp2d_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit('shaderSpaceOptionIntOptVars', 4, 
                str(idx)))
        self.channel_gb = QtGui.QGroupBox('Options')
        self.channel_gb.setAlignment(QtCore.Qt.AlignCenter)
        self.channel_gb.setLayout(self.channel_vl)
        return self.channel_gb

    def _vauleField(self):
        bump_valid = QtGui.QRegExpValidator(QtCore.QRegExp(r'(0|1)\.\d{1,3}'))
        filterIndex = _PRESERVE['shaderSpaceFilterTypeIntOptVar']
        bumpValue   = _PRESERVE['shaderSpaceBumpValueFloatOptVar']
        alphaIsLum  = _PRESERVE['shaderSpaceAlphaIsLuminanceIntOptVar']
        # Create
        self.bumpvaule_le = QtGui.QLineEdit(str(bumpValue))
        self.bumpvaule_le.setMaximumWidth(60)
        self.bumpvaule_le.setValidator(bump_valid)
        self.filter_cbb = QtGui.QComboBox()
        self.filter_cbb.addItems(
            ('off', 'Mipmap', 'Box', 'Quadratic', 'Quartic', 'Gaussian'))
        self.filter_cbb.setCurrentIndex(filterIndex)
        self.alphaIsLum_cb = QtGui.QCheckBox()
        if alphaIsLum:
            self.alphaIsLum_cb.setCheckState(QtCore.Qt.Checked)
        else:
            self.alphaIsLum_cb.setCheckState(QtCore.Qt.Unchecked)
        # Layout
        self.value_gb = QtGui.QGroupBox('Values')
        self.value_gb.setAlignment(QtCore.Qt.AlignCenter)
        self.main_fl = QtGui.QFormLayout()
        self.main_fl.addRow('Bump Value', self.bumpvaule_le)
        self.main_fl.addRow('Filter Type', self.filter_cbb)
        self.main_fl.addRow('Alpha is Lim', self.alphaIsLum_cb)
        self.value_gb.setLayout(self.main_fl)
        # Connect
        self.bumpvaule_le.textEdited.connect(
            lambda t: self.sender.emit(
                'shaderSpaceBumpValueFloatOptVar', 0, str(t)))
        self.filter_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceFilterTypeIntOptVar', 0, str(idx)))
        self.alphaIsLum_cb.stateChanged.connect(
            lambda state: self.sender.emit(
                'shaderSpaceAlphaIsLuminanceIntOptVar', 0, str(state)))
        self.bumpvaule_le.textEdited.connect(self._checkEmpty)
        return self.value_gb

    def _shadersField(self):
        shader_index = _PRESERVE['shaderSpaceShaderIntOptVar']
        # Component
        self.shader_cbb = QtGui.QComboBox()
        self.shader_cbb.addItems(kShadersList)
        self.shader_cbb.setCurrentIndex(shader_index)
        self.shader_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceShaderIntOptVar', 0, str(idx)))
        self.preset_cbb = QtGui.QComboBox()
        self._resetPresets(kShadersList[shader_index])
        # Layout
        self.shader_gb = QtGui.QGroupBox('Shaders')
        self.shader_gb.setAlignment(QtCore.Qt.AlignCenter)
        self.shader_fl = QtGui.QFormLayout()
        self.shader_fl.addRow('Shader Selections', self.shader_cbb)
        self.shader_fl.addRow('Shader Presets', self.preset_cbb)
        self.shader_gb.setLayout(self.shader_fl)
        # Color Management components for up to Maya 2015, 2016
        if kMayaVersion in ('2015', '2016'):
            name_buff = _PRESERVE['shaderSpaceColorProfileNameStrOptVars']
            sRgbColorSpaceName = name_buff[0]
            linearColorSpaceName = name_buff[1]
            self.sRgbColorSpace_cbb = QtGui.QComboBox()
            self.linearColorSpace_cbb = QtGui.QComboBox()
            cmPrefs = mc.colorManagementPrefs(q=True, inputSpaceNames=True)
            self.sRgbColorSpace_cbb.addItems(cmPrefs)
            self.linearColorSpace_cbb.addItems(cmPrefs)
            sRgb_idx = self.sRgbColorSpace_cbb.findText(
                sRgbColorSpaceName, QtCore.Qt.MatchFixedString)
            if sRgb_idx >= 0:
                self.sRgbColorSpace_cbb.setCurrentIndex(sRgb_idx)
            linear_idx = self.linearColorSpace_cbb.findText(
                linearColorSpaceName, QtCore.Qt.MatchFixedString)
            if linear_idx >= 0:
                self.linearColorSpace_cbb.setCurrentIndex(linear_idx)
            # connect
            self.sRgbColorSpace_cbb.activated[str].connect(
                lambda name: self.sender.emit(
                    'shaderSpaceColorProfileNameStrOptVars', 0, str(name)))
            self.linearColorSpace_cbb.activated[str].connect(
                lambda name: self.sender.emit(
                    'shaderSpaceColorProfileNameStrOptVars', 0, str(name)))
            self.shader_fl.addRow('sRGB', self.sRgbColorSpace_cbb)
            self.shader_fl.addRow('Linear', self.linearColorSpace_cbb)
        #
        for idx in range(self.shader_fl.count()):
            widget = self.shader_fl.itemAt(idx).widget()
            if isinstance(widget, QtGui.QComboBox):
                widget.setMinimumHeight(24)
                widget.setSizePolicy(QtGui.QSizePolicy.Expanding, 
                                     QtGui.QSizePolicy.Preferred)
        # Connect
        self.shader_cbb.activated[str].connect(
            lambda shaderType: self._resetPresets(shaderType))
        self.preset_cbb.activated[str].connect(
            lambda preset: self._updatePreset(preset))
        return self.shader_gb

    def _executeField(self):
        # Widget
        self.createShaderButton = QtGui.QPushButton('Create Shader')
        self.createShaderButton.setMinimumHeight(42)
        self.createShaderButton.setMinimumWidth(100)
        # Layout
        self.execute_vl = QtGui.QVBoxLayout()
        self.execute_vl.addWidget(self.createShaderButton)
        self.execute_fr = QtGui.QFrame()
        self.execute_fr.setLayout(self.execute_vl)
        # Connect
        self.createShaderButton.clicked.connect(_createShader)
        return self.execute_fr

    def _checkEmpty(self, context):
        if not context:
            self.createShaderButton.setEnabled(False)
        else:
            self.createShaderButton.setEnabled(True)

    def _updatePreset(self, preset):
        _SHADER_PRESET = preset

    def _resetPresets(self, shaderType):
        self.preset_cbb.clear()
        self.preset_cbb.addItem('No Preset')
        search_dir = self._presetsDir+'/'+shaderType
        if not isdir(search_dir):
            return []
        presets_set = []
        for mel in listdir(search_dir):
            buff = splitext(mel)
            if buff[1] == '.mel':
                presets_set.append(buff[0])
        if presets_set:
            self.preset_cbb.addItems(presets_set)

class ShaderSpaceUVsWin(QtGui.QWidget):
    sender = QtCore.Signal(str, int, str)
    global _PRESERVE
    UV_SNAPSHOT_EXTS = ('png', 'tif', 'jpg', 'tga', 'bmp')
    RESOLUTIONS = ('512', '1024', '2048', '4096')
    COLORS = ('Black', 'White', 'Red')
    MODES = ('Visible Display Layers', 'Sets', 'From Selected')
    def __init__(self, parent=None):
        super(ShaderSpaceUVsWin, self).__init__(parent)
        self.sender.connect(_updateOptionVarsSlot)
        self.initUI()

    def initUI(self):
        options = copy.deepcopy(
            _PRESERVE['shaderSpaceUvSnapshotOptionIntOptVars'])
        init_path = _PRESERVE['shaderSpaceToolsPathStrOptVars'][0]
        self.main_vl = QtGui.QVBoxLayout()
        # Group
        self.main_gb = QtGui.QGroupBox('Batch UV Snapshot')
        self.main_gb.setAlignment(QtCore.Qt.AlignCenter)
        # Component
        self.path_le = QtGui.QLineEdit(init_path)
        self.path_le.setMinimumSize(300, 30)
        self.path_le.textChanged.connect(lambda t: self.sender.emit(
            'shaderSpaceToolsPathStrOptVars', 0, str(t)))
        self.browse_btn = QtGui.QPushButton('...')
        self.browse_btn.setMinimumWidth(40)
        self.ext_cbb = QtGui.QComboBox()
        self.ext_cbb.addItems(self.UV_SNAPSHOT_EXTS)
        self.ext_cbb.setMinimumSize(120, 28)
        self.res_cbb = QtGui.QComboBox()
        self.res_cbb.addItems(self.RESOLUTIONS)
        self.res_cbb.setMinimumSize(120, 28)
        self.color_cbb = QtGui.QComboBox()
        self.color_cbb.addItems(self.COLORS)
        self.color_cbb.setMinimumSize(120, 28)
        self.source_cbb = QtGui.QComboBox()
        self.source_cbb.addItems(self.MODES)
        self.source_cbb.setMinimumSize(160, 28)
        # Set default
        self.ext_cbb.setCurrentIndex(options[0])
        self.res_cbb.setCurrentIndex(options[1])
        self.color_cbb.setCurrentIndex(options[2])
        self.source_cbb.setCurrentIndex(options[3])
        self.make_btn = QtGui.QPushButton('Snapshot')
        self.make_btn.setMinimumSize(120, 30)
        # Layout
        self.dir_hl = QtGui.QHBoxLayout()
        self.dir_hl.addWidget(self.path_le)
        self.dir_hl.addWidget(self.browse_btn)
        self.main_fl = QtGui.QFormLayout()
        self.main_fl.setFormAlignment(QtCore.Qt.AlignRight)
        self.main_fl.setHorizontalSpacing(10)
        self.main_fl.addRow('Export Path',      self.dir_hl)
        self.main_fl.addRow('Extension',        self.ext_cbb)
        self.main_fl.addRow('Resolutions',      self.res_cbb)
        self.main_fl.addRow('Color Choice',     self.color_cbb)
        self.main_fl.addRow('Snapshot Source',  self.source_cbb)
        self.main_fl.addRow(self.make_btn)
        self.main_gb.setLayout(self.main_fl)
        self.main_vl.addWidget(self.main_gb)
        # Connect
        self.browse_btn.clicked.connect(
            partial(_folderDialog, self.path_le, 'UV Snapshot Directory', self))
        self.ext_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceUvSnapshotOptionIntOptVars', 0, str(idx)))
        self.res_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceUvSnapshotOptionIntOptVars', 1, str(idx)))
        self.color_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceUvSnapshotOptionIntOptVars', 2, str(idx)))
        self.source_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpaceUvSnapshotOptionIntOptVars', 3, str(idx)))
        self.make_btn.clicked.connect(self._do_uvsnapshot)
        # Set main layout
        self.setLayout(self.main_vl)

    def _do_uvsnapshot(self):
        save_path = self.path_le.text().replace('\\', '/')
        ext = self.UV_SNAPSHOT_EXTS[self.ext_cbb.currentIndex()]
        res = self.RESOLUTIONS[self.res_cbb.currentIndex()]
        color = self.COLORS[self.color_cbb.currentIndex()]
        source = self.source_cbb.currentIndex()
        tools.uvSnapshot(save_path, ext, res, color, source)

class ShaderSpaceMeshExportWin(QtGui.QWidget):
    sender = QtCore.Signal(str, int, str)
    global _PRESERVE
    DATA_TYPE = ('Maya Ascii', 'Maya Binary', 'OBJ')
    MODES = ('Visible Display Layers', 'Sets', 'From selected')
    def __init__(self, parent=None):
        super(ShaderSpaceMeshExportWin, self).__init__(parent)
        self.sender.connect(_updateOptionVarsSlot)
        self.initUI()

    def initUI(self):
        global _LINE_EDIT_HEIGHT
        options  = _PRESERVE['shaderSpacePolygonExportOptionIntOptVars']
        inexclude= _PRESERVE['shaderSpacePolygonExportOptionStrOptVars']
        init_path= _PRESERVE['shaderSpaceToolsPathStrOptVars'][1]
        #
        self.main_vl = QtGui.QVBoxLayout()
        self.main_vl.setAlignment(QtCore.Qt.AlignRight)
        self.main_fl = QtGui.QFormLayout()
        self.dir_hl  = QtGui.QHBoxLayout()
        self.main_gb = QtGui.QGroupBox('Export Mesh')
        self.main_gb.setAlignment(QtCore.Qt.AlignCenter)
        # Component
        self.path_le = QtGui.QLineEdit(init_path)
        self.path_le.setMinimumHeight(_LINE_EDIT_HEIGHT)
        self.browse_btn = QtGui.QPushButton('...')
        self.mode_cbb = QtGui.QComboBox()
        self.mode_cbb.setMinimumSize(160, 28)
        self.source_cbb = QtGui.QComboBox()
        self.source_cbb.setMinimumSize(160, 28)
        self.exclude_le = QtGui.QLineEdit(inexclude[0])
        self.exclude_le.setMinimumHeight(_LINE_EDIT_HEIGHT)
        self.exclude_le.setMaximumWidth(120)
        self.include_le = QtGui.QLineEdit(inexclude[1])
        self.include_le.setMinimumHeight(_LINE_EDIT_HEIGHT)
        self.include_le.setMaximumWidth(120)
        self.make_btn = QtGui.QPushButton('Export')
        self.make_btn.setMinimumHeight(30)
        self.mode_cbb.addItems(self.DATA_TYPE)
        self.source_cbb.addItems(self.MODES)
        self.browse_btn.setMinimumSize(36, 28)
        self.mode_cbb.setCurrentIndex(options[0])
        # Layout
        self.main_vl.addWidget(self.main_gb)
        self.main_gb.setLayout(self.main_fl)
        self.dir_hl.addWidget(self.path_le)
        self.dir_hl.addWidget(self.browse_btn)
        self.main_fl.addRow('Export Path',      self.dir_hl)
        self.main_fl.addRow('Data Type',        self.mode_cbb)
        self.main_fl.addRow('Source',           self.source_cbb)
        self.main_fl.addRow('Exclude string',   self.exclude_le)
        self.main_fl.addRow('Include string',   self.include_le)
        self.main_fl.addRow(self.make_btn)
        # Connect
        self.browse_btn.clicked.connect(
            partial(_folderDialog, self.path_le, 'Export Directory', self))
        self.path_le.textChanged.connect(
            lambda t: self.sender.emit('shaderSpaceToolsPathStrOptVars', 1, 
                str(t)))
        self.mode_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpacePolygonExportOptionIntOptVars', 0, str(idx)))
        self.source_cbb.currentIndexChanged.connect(
            lambda idx: self.sender.emit(
                'shaderSpacePolygonExportOptionIntOptVars', 1, str(idx)))
        self.exclude_le.textEdited.connect(
            lambda t: self.sender.emit(
                'shaderSpacePolygonExportOptionStrOptVars', 0, str(t)))
        self.include_le.textEdited.connect(
            lambda t: self.sender.emit(
                'shaderSpacePolygonExportOptionStrOptVars', 1, str(t)))
        self.make_btn.clicked.connect(self._do_exportPolygons)
        # set main layout
        self.setLayout(self.main_vl)

    def _do_exportPolygons(self):
        save_path = self.path_le.text().replace('\\', '/')
        include = self.include_le.text()
        exclude = self.exclude_le.text()
        save_type = self.DATA_TYPE[self.mode_cbb.currentIndex()]
        source = self.source_cbb.currentIndex()
        tools.exportPolygons(save_path, save_type, include, exclude, source)

class ShaderSpacePsdWin(QtGui.QWidget):
    global _PRESERVE
    sender = QtCore.Signal(str, int, str)
    RESOLUTIONS = ('512', '1024', '2048', '4096')
    HEADER = ('PSD', 'UV', 'Resolution')
    IMG_FILTER = 'Photoshop file (*.psd)'
    UV_FILTER = 'Images (*.png *.jpg *.tif *.tga *.bmp)'
    def __init__(self, parent=None):
        super(ShaderSpacePsdWin, self).__init__(parent)
        self.sender.connect(_updateOptionVarsSlot)
        self.initUI()

    def initUI(self):
        global _LINE_EDIT_HEIGHT
        ps_path = _PRESERVE['shaderSpaceToolsPathStrOptVars'][2]
        uv_path = _PRESERVE['shaderSpaceToolsPathStrOptVars'][4]
        # Group
        self.main_vl = QtGui.QVBoxLayout()
        self.main_fl = QtGui.QFormLayout()
        self.main_gb = QtGui.QGroupBox('Photoshop File Generate')
        self.main_gb.setAlignment(QtCore.Qt.AlignCenter)
        self.psdir_hl = QtGui.QHBoxLayout()
        self.uvdir_hl = QtGui.QHBoxLayout()
        self.chs_hl   = QtGui.QHBoxLayout()
        # Component
        self.path_le = QtGui.QLineEdit(ps_path)
        self.path_le.setMinimumHeight(_LINE_EDIT_HEIGHT)
        self.browse_btn = QtGui.QPushButton('...')
        self.browse_btn.setMinimumWidth(40)
        self.uvbrowse_btn = QtGui.QPushButton('...')
        self.uvbrowse_btn.setMinimumWidth(40)
        self.uvpath_le = QtGui.QLineEdit(uv_path)
        self.uvpath_le.setMinimumHeight(_LINE_EDIT_HEIGHT)
        self.res_cbb = QtGui.QComboBox()
        self.res_cbb.addItems(self.RESOLUTIONS)
        self.res_cbb.setMinimumSize(120, 32)
        self.chsHint_lb = QtGui.QLabel()
        self._reset_chsHint()
        self.refresh_btn = QtGui.QPushButton('Refresh')
        self.refresh_btn.setMinimumSize(120, 30)
        self.refresh_btn.setSizePolicy(QtGui.QSizePolicy.Maximum, 
                                       QtGui.QSizePolicy.Maximum)
        self.chs_hl.addWidget(self.chsHint_lb)
        self.chs_hl.addWidget(self.refresh_btn)
        self.make_btn = QtGui.QPushButton('Generate')
        self.make_btn.setMinimumHeight(30)
        self.main_fl.addRow('Photoshop File', self.psdir_hl)
        self.main_fl.addRow('UV Image File', self.uvdir_hl)
        self.main_fl.addRow('Image Resolution', self.res_cbb)
        self.main_fl.addRow('Channels : ', self.chs_hl)
        self.main_vl.addWidget(self.main_gb)
        self.psdir_hl.addWidget(self.path_le)
        self.psdir_hl.addWidget(self.browse_btn)
        self.uvdir_hl.addWidget(self.uvpath_le)
        self.uvdir_hl.addWidget(self.uvbrowse_btn)
        self.main_fl.addRow(self.make_btn)
        #
        self.main_gb.setLayout(self.main_fl)
        # Connect
        self.path_le.textChanged.connect(
            lambda t: self.sender.emit(
                'shaderSpaceToolsPathStrOptVars', 2, str(t)))
        self.uvpath_le.textChanged.connect(
            lambda t: self.sender.emit(
                'shaderSpaceToolsPathStrOptVars', 4, str(t)))
        self.browse_btn.clicked.connect(
            partial(_saveFileDialog, self.path_le, self.IMG_FILTER, '', 
                'Save Photoshop File'))
        self.uvbrowse_btn.clicked.connect(
            partial(_openFileDialog, self.uvpath_le, self.UV_FILTER, '',
                'UV Image Directory'))
        self.refresh_btn.clicked.connect(self._reset_chsHint)
        self.make_btn.clicked.connect(self._do_photoshop_file)
        self.setLayout(self.main_vl)

    def _reset_chsHint(self):
        save_abbreviations = copy.deepcopy(
            _PRESERVE['shaderSpaceAbbreviationsStrOptVars'])
        abbreviations = []
        abbreviations_hint = 'No channel names append'
        for idx, c in enumerate(_PRESERVE['shaderSpaceChannelsIntOptVars']):
            if not c: continue
            abbreviations.append(save_abbreviations[idx])
        if abbreviations:
            abbreviations_hint = ', '.join(abbreviations)
        self.chsHint_lb.setText(abbreviations_hint)
        print abbreviations_hint
        return abbreviations

    def _do_photoshop_file(self):
        psd_file = self.path_le.text()
        uv_file = self.uvpath_le.text()
        abbreviations = self._reset_chsHint()
        resolution = self.RESOLUTIONS[self.res_cbb.currentIndex()]
        tools.createPhotoshopFile(psd_file, uv_file, abbreviations, resolution)

class ShaderSpaceBakerWin(QtGui.QWidget):
    sender = QtCore.Signal(str, int, str)
    RESOLUTIONS = (512, 1024, 2048, 4096)
    def __init__(self, parent=None):
        super(ShaderSpaceBakerWin, self).__init__(parent)
        self.sender.connect(_updateOptionVarsSlot)
        self.initUI()

    def initUI(self):
        global _LINE_EDIT_HEIGHT, _VAILD_WIN_FILE_NAME
        # The Lambda to set widget size
        self.main_fl  = QtGui.QFormLayout()
        self.dir_hl  = QtGui.QHBoxLayout()
        self.bake_dir_le = QtGui.QLineEdit()
        self.bake_dir_le.setMinimumHeight(_LINE_EDIT_HEIGHT)
        self.bake_img_le = QtGui.QLineEdit()
        self.bake_img_le.setMinimumHeight(_LINE_EDIT_HEIGHT)
        self.bake_img_le.setValidator(_VAILD_WIN_FILE_NAME)
        self.browse_btn = QtGui.QPushButton('...')
        self.browse_btn.setMinimumWidth(32)
        self.resolution_cbb = QtGui.QComboBox()
        self.resolution_cbb.setMinimumSize(120, 30)
        self.resolution_cbb.addItems(('512', '1024', '2048', '4096'))
        self.bake_btn = QtGui.QPushButton('Bake Turtle AO')
        self.bake_btn.setFixedHeight(32)
        self.bake_btn.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                    QtGui.QSizePolicy.Fixed)
        self.dir_hl.addWidget(self.bake_dir_le)
        self.dir_hl.addWidget(self.browse_btn)
        self.main_fl.addRow('Bake Directory', self.dir_hl)
        self.main_fl.addRow('Bake Image Name', self.bake_img_le)
        self.main_fl.addRow('Image Resolution', self.resolution_cbb)
        self.main_fl.addRow(self.bake_btn)
        # connect
        self.browse_btn.clicked.connect(
            partial(_folderDialog, self.bake_dir_le, 
                'Bake Image Directory', self))
        self.bake_btn.clicked.connect(partial(self.bake, 'Turtle AO'))
        #
        self.setLayout(self.main_fl)

    def bake(self, method):
        directory = self.bake_dir_le.text().replace('\\', '/')
        if not isdir(directory):
            print '# {0} is can not be access or not exists!'.format(directory)
            return -1
        img_name = self.bake_img_le.text()
        img_file = self.bake_img_le.text().replace(" ", "")
        if not img_file:
            print '# Bake file name can not be empty!'
            return -1
        resolution = self.RESOLUTIONS[self.resolution_cbb.currentIndex()]
        resolution = (resolution, resolution)
        ilrocc.bake(directory, img_name, resolution)

class ShaderSpaceSettingWin(QtGui.QWidget):
    global _PRESERVE
    global kChannelList
    sender = QtCore.Signal(str, int, str)
    NOTES = '''
    <asset> Asset Name
    <shader> Shader Name
    <user> User Name
    <version> Version
    <channel> Channel Abbreviations(texture and p2d only)
    '''
    def __init__(self, parent=None):
        super(ShaderSpaceSettingWin, self).__init__(parent)
        self.sender.connect(_updateOptionVarsSlot)
        self.initUI()

    def initUI(self):
        self.main_vl = QtGui.QVBoxLayout()
        self._buildNodes()
        self._buildRules()
        self._buildAbbreviations()
        self.main_vl.addWidget(self.nodes_gb)
        self.main_vl.addWidget(self.rule_gb)
        self.main_vl.addWidget(self.abbrev_gb)
        self.setLayout(self.main_vl)

    def _buildNodes(self):
        global _PRESERVE
        rules = copy.deepcopy(
            _PRESERVE['shaderSpaceNodeNameRuleStrOptVars'])
        # Component
        self.shader_le  = QtGui.QLineEdit(rules[0])
        self.shading_le = QtGui.QLineEdit(rules[1])
        self.texture_le = QtGui.QLineEdit(rules[2])
        self.bump2d_le  = QtGui.QLineEdit(rules[3])
        self.place2d_le = QtGui.QLineEdit(rules[4])
        self.mtinfo_le  = QtGui.QLineEdit(rules[5])
        # Layout
        self.nodes_gb = QtGui.QGroupBox('Maya Nodes')
        self.nodes_gb.setAlignment(QtCore.Qt.AlignCenter)
        self.nodes_fl = QtGui.QFormLayout()
        self.nodes_fl.addRow('Shader',          self.shader_le)
        self.nodes_fl.addRow('Texture',         self.texture_le)
        self.nodes_fl.addRow('Bump2d',          self.bump2d_le)
        self.nodes_fl.addRow('Place2dTexture',  self.place2d_le)
        self.nodes_fl.addRow('Material Info',   self.mtinfo_le)
        # Set
        for idx in range(self.nodes_fl.count()):
            widget = self.nodes_fl.itemAt(idx).widget()
            if isinstance(widget, QtGui.QLineEdit):
                widget.setMinimumHeight(28)
                widget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Fixed)
        self.setLayout(self.nodes_fl)
        self.nodes_gb.setToolTip(self.NOTES)
        self.nodes_gb.setLayout(self.nodes_fl)
        # Connect
        self.shader_le.textEdited.connect(
            lambda text: self.sender.emit(
                'shaderSpaceNodeNameRuleStrOptVars', 0, str(text)))
        self.shading_le.textEdited.connect(
            lambda text: self.sender.emit(
                'shaderSpaceNodeNameRuleStrOptVars', 1, str(text)))
        self.texture_le.textEdited.connect(
            lambda text: self.sender.emit(
                'shaderSpaceNodeNameRuleStrOptVars', 2, str(text)))
        self.bump2d_le.textEdited.connect(
            lambda text: self.sender.emit(
                'shaderSpaceNodeNameRuleStrOptVars', 3, str(text)))
        self.place2d_le.textEdited.connect(
            lambda text: self.sender.emit(
                'shaderSpaceNodeNameRuleStrOptVars', 4, str(text)))
        self.mtinfo_le.textEdited.connect(
            lambda text: self.sender.emit(
                'shaderSpaceNodeNameRuleStrOptVars', 5, str(text)))

    def _buildRules(self):
        global _LINE_EDIT_HEIGHT
        _buildRules = _PRESERVE['shaderSpaceAutoPathRuleStrOptVar']
        # Component
        self.texture_path_rule_le = QtGui.QLineEdit(_buildRules)
        # Set attribute
        self.texture_path_rule_le.setMinimumHeight(_LINE_EDIT_HEIGHT)
        self.texture_path_rule_le.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                                QtGui.QSizePolicy.Fixed)
        # Layout
        self.rule_hl = QtGui.QHBoxLayout()
        self.rule_hl.addWidget(QtGui.QLabel('Texture Path Rule'))
        self.rule_hl.addWidget(self.texture_path_rule_le)
        self.rule_gb = QtGui.QGroupBox('Auto Texture Path')
        self.rule_gb.setAlignment(QtCore.Qt.AlignCenter)
        self.rule_gb.setToolTip(self.NOTES)
        self.rule_gb.setLayout(self.rule_hl)
        # Connect
        self.texture_path_rule_le.textEdited.connect(
            lambda text: self.sender.emit(
                'shaderSpaceAutoPathRuleStrOptVar', 0, str(text)))

    def _buildAbbreviations(self):
        abbreviations = copy.deepcopy(
            _PRESERVE['shaderSpaceAbbreviationsStrOptVars'])
        self.abbrev_gb = QtGui.QGroupBox('Channel Abbreviations')
        self.abbrev_gb.setAlignment(QtCore.Qt.AlignCenter)
        self.abbrev_gl = QtGui.QGridLayout()
        self.abbreviations = []
        for col in range(4):
            for row in range(6):
                index = (col*3) + (row/2)
                if row % 2 == 0:
                    self.abbrev_gl.addWidget(
                        QtGui.QLabel(kChannelList[index]), col, row)
                else:
                    field = QtGui.QLineEdit(abbreviations[index])
                    field.setValidator(_VAILD_MAYA_NODE_NAME)
                    field.setMaximumWidth(80)
                    field.textEdited.connect(
                        lambda text, index=index: self.sender.emit(
                            'shaderSpaceAbbreviationsStrOptVars', index, 
                                str(text)))
                    self.abbrev_gl.addWidget(field, col, row)
                    field.setMinimumHeight(24)
                    field.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Fixed)
        self.abbrev_gb.setLayout(self.abbrev_gl)

# Maya Python end
