# -*- coding: utf-8 -*-
# shaderSpace utility swatches degamma append
#
# Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
#
# E-Mail : nnnight@gmail.com
#
# Github : http://github.com/chiaxin
#
# Licensed under MIT: https://opensource.org/licenses/MIT
#
import maya.cmds as mc
import maya.OpenMayaUI as omui
from functools import partial
from config import *
if kMayaVersionNumber >= 2017:
    import PySide2.QtWidgets as QtGui
    import PySide2.QtGui as QtGui4
    from PySide2 import QtCore
    from shiboken2 import wrapInstance
else:
    from PySide import QtGui, QtCore
    from shiboken import wrapInstance
#from PySide import QtCore, QtGui
#from shiboken import wrapInstance

GAMMA_VALUE = 0.4545

def getUseColorWritableAttributes(node):
    if not mc.objExists(node):
        raise ValueError('Can not find node : {0}'.format(node))
    all_useColor_attributes = \
    [ a for a in mc.attributeInfo(node, writable=True) \
    if mc.attributeQuery(a, n=node, usedAsColor=True) ]
    # -
    if all_useColor_attributes:
        return all_useColor_attributes
    return []

def getColorAttrsIsNotSolidWhiteOrBlack(node):
    color_attributes = getUseColorWritableAttributes(node)
    collections = []
    for attr in color_attributes:
        # If attribute has been connected with another, skip it.
        if mc.listConnections(node+'.'+attr, s=True, d=False):
            continue
        # Get color values
        color_values = mc.getAttr(node+'.'+attr)[0]
        # Check if this attribute is vector of 3 elements
        if isinstance(color_values, tuple) and len(color_values) == 3:
            # Check this color is not solid white or black
            if color_values[0] != 0.0 and color_values[0] != 1.0 \
            or color_values[1] != 0.0 and color_values[1] != 1.0 \
            or color_values[2] != 0.0 and color_values[2] != 1.0:
                # If so, add it
                collections.append(attr)
    if collections:
        return collections
    return []

def createDegammaNodeAndConnect(target):
    global GAMMA_VALUE
    if not mc.objExists(target):
        return ''
    if mc.listConnections(target, s=True):
        mc.warning('# {0} has been connected!'.format(target))
        return ''
    gcname = target.replace('.', '_') + '_GC'
    degamma_node = mc.shadingNode('gammaCorrect', name=gcname, asUtility=True)
    mc.setAttr(degamma_node+'.gammaX', GAMMA_VALUE)
    mc.setAttr(degamma_node+'.gammaY', GAMMA_VALUE)
    mc.setAttr(degamma_node+'.gammaZ', GAMMA_VALUE)
    values = mc.getAttr(target)[0]
    mc.setAttr(degamma_node+'.value', 
       values[0], values[1], values[2], type='double3')
    mc.connectAttr(degamma_node+'.outValue', target, force=True)
    return degamma_node

class SwatchesDegammaWin(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SwatchesDegammaWin, self).__init__(parent)
        self.node = ''
        self.setWindowTitle('Attribute Choice')
        self.setMinimumSize(QtCore.QSize(240, 120))
        self.initUI()

    def initUI(self):
        attrs = self.getNeedToDegammaAttrs()
        self.close_btn = QtGui.QPushButton('Close')
        self.close_btn.setMaximumWidth(60)
        self.main_vl = QtGui.QVBoxLayout()
        self.main_vl.addWidget(QtGui.QLabel('<Item> '+self.node))
        if self.node:
            self.main_vl.addWidget(QtGui.QLabel(
                '<Type> '+mc.nodeType(self.node)))
        if not attrs:
            self.main_vl.addWidget(QtGui.QLabel(
                'No any attributes need to degamma'))
        else:
            for attr in attrs:
                target = self.node + '.' + attr
                button = QtGui.QPushButton(attr)
                button.clicked.connect(
                    partial(createDegammaNodeAndConnect, target))
                button.clicked.connect(
                    lambda btn=button: btn.setDisabled(True))
                self.main_vl.addWidget(button)
        self.main_vl.addWidget(self.close_btn)
        # Connect
        self.close_btn.clicked.connect(self.close)
        self.setLayout(self.main_vl)

    def getNeedToDegammaAttrs(self):
        selections = mc.ls(sl=True)
        if selections:
            first_selected = selections[0]
            attributes = getColorAttrsIsNotSolidWhiteOrBlack(first_selected)
            self.node = first_selected
            return attributes
        else:
            return ''
