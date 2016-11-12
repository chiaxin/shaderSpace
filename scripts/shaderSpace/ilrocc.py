# -*- coding: utf-8 -*-
# shaderSpace Turtle Bake Ambient Occlusion
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
import maya.mel as mel
import os.path

class BakeTurtleAO():
    kEnableSelfOcc = 2
    kDisableSelfOcc= 0
    kMinColor = (0.1, 0.1, 0.1)
    def __init__(self, dir, img='ilrBakeMap', size=(2048, 2048)):
        self.is_plugin_loaded = mc.pluginInfo('Turtle', q=True, loaded=True)
        self.directory = dir
        self.img_name = img
        self.size = size
        self.collection_shape = list()

    def loadTurtlePlugin(self):
        if not self.is_plugin_loaded:
            try:
                mc.loadPlugin('Turtle')
            except:
                print '# Failed to load Turtle plug-in'
            else:
                self.is_plugin_loaded = True

    def createIlrOccSampler(self, selfOcc=kEnableSelfOcc):
        pre_selections = mc.ls(sl=True, l=True)
        if not self.is_plugin_loaded:
            print '# Please load Turtle plug-in'
            return ''
        try:
            ilrOccSampler = mc.shadingNode('ilrOccSampler', asShader=True)
            mc.setAttr(ilrOccSampler+'.type', 1)
            mc.setAttr(ilrOccSampler+'.minColor',
                       self.kMinColor[0],
                       self.kMinColor[1],
                       self.kMinColor[2],
                       type='double3')
        except:
            print '# Failed to create ilrOccSampler Node!'
            raise
        finally:
            mc.select(pre_selections, r=True)
        return ilrOccSampler

    def getLeafShape(self, items):
        for member in items:
            # Get all shape children into sets
            under_member = mc.listRelatives(member, ad=True, f=True)
            if not under_member:
                self.collection_shape.append(member)
            else:
                children = [c for c in under_member if mc.nodeType(c) == 'mesh']
                self.collection_shape.extend(children)
        if not self.collection_shape:
            print '{0} have no any shape members'.format(displayLayer)
        return self.collection_shape

    def turtleAOBakeProcess(self):
        if not self.img_name:
            bake_name = 'turtleBakeAOMap'
        else:
            bake_name = self.img_name
        if not os.path.isdir(self.directory):
            print '{0} folder can not be bake!'.format(self.dir)
            return ''
        try:
            self.loadTurtlePlugin()
        except:
            print 'failed in load plugin'
            raise
        try:
            ilrOccSampler = self.createIlrOccSampler()
        except:
            print 'failed in ilr occ sampler'
            raise
        bake_script = ['ilrTextureBakeCmd']
        for mesh in self.collection_shape:
            bake_script.append('-target \"{0}\"'.format(mesh))
        bake_script.append('-backgroundColor 1 1 1')
        bake_script.append('-width '+str(self.size[0]))
        bake_script.append('-height '+str(self.size[1]))
        bake_script.append('-saveToFile 1')
        bake_script.append('-directory \"'+self.directory.replace('\\', '/')+'\"')
        bake_script.append('-fileName '+self.img_name+'.tif')
        bake_script.append('-fileFormat 4')
        bake_script.append('-merge 1')
        bake_script.append('-camera persp')
        bake_script.append('-custom 1')
        occ_sampler = self.createIlrOccSampler()
        bake_script.append('-customShader '+ilrOccSampler)
        final_bake_script = ' '.join(bake_script)
        try:
            mel.eval(final_bake_script)
        except:
            print '# Failed to execute Turtle bake!'
            raise
        else:
            print '# Bake Turtle AO Map successiful!'
        finally:
            mc.delete(ilrOccSampler)

    def turtleAOBakeSelected(self):
        selections = mc.ls(sl=True, l=True)
        if not selections:
            return ''
        self.getLeafShape(selections)
        if not self.collection_shape:
            print '# No any shape can be bake'
            return ''
        try:
            self.turtleAOBakeProcess()
        except:
            raise

def bake(dir, img, size):
    if not dir or not img:
        return
    bake_instance = BakeTurtleAO(dir, img, size)
    try:
        bake_instance.turtleAOBakeSelected()
    except:
        raise
