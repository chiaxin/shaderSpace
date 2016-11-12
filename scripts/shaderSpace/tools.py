# -*- coding: utf-8 -*-
# Tools for shaderSpace
#
# Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
#
# E-Mail : nnnight@gmail.com
#
# Github : http://github.com/chiaxin
#
# Licensed under MIT: https://opensource.org/licenses/MIT
#
from os import listdir
from os.path import isfile, isdir, dirname, exists
from config import kChannelList
import maya.cmds as mc
import maya.mel as mel

def exportShaders(export_path, mode):
    if not export_path:
        mc.warning('Please enter a output folder!')
        return -1
    if not exists(export_path):
        mc.warning('Directory is not exists :'+export_path)
        return -1
    shading_groups = []
    if mode == 0:
        shading_groups = [s for s in mc.ls(type='shadingEngine')
            if s not in ('initialParticleSE', 'initialShadingGroup')]
    elif mode == 1:
        selections = mc.ls(sl=True)
        if not selections:
            mc.warning(
                'Please select at least one shader or mesh, nurbsShapes.')
            return -1
        for sel in selections:
            connected_sg = mc.listConnections(sel, s=False,
                d=True, type='shadingEngine')
            if not connected_sg:
                continue
            shading_groups.extend([s for s in connected_sg
                if s not in ('initialParticleSE', 'initialShadingGroup')])
        shading_groups = list(set(shading_groups))
    else:
        return -1
    if not shading_groups:
        mc.warning('There are no any shaders can be export!')
        return -1
    if not _userConfirm('Export Shaders', '\n'.join(shading_groups)):
        return -1
    connections = []
    fullpath = ''
    amout = 0
    process_max = len(shading_groups)
    mc.progressWindow(title='Export Shaders', progress=amout,
        status='Export start...', isInterruptable=True, max=process_max)
    for sg in shading_groups:
        if mc.progressWindow(q=True, isCancelled=True):
            break
        fullpath = '{0}{1}.ma'.format(export_path, sg.replace(':', '_'))
        connections = mc.listHistory(sg, allFuture=True, pruneDagObjects=True)
        mc.select(connections, replace=True, noExpand=True)
        try:
            mc.file(fullpath, force=True, exportSelected=True,
                type='mayaAscii', options='v=0;')
            amout += 1
            mc.progressWindow(e=True, progress=amout, 
                status='Export : {0} / {1}'.format(amout,  process_max))
        except:
            raise
        mc.select(cl=True)
    mc.progressWindow(endProgress=True)

def exportPolygons(export_path, export_type, exclude, include, source):
    if not export_path:
        mc.warning('Please enter a output folder!')
        return -1
    elif not exists(export_path):
        mc.warning('Directory is not exists : {0}'.format(export_path))
        return -1
    objExportPlugin = mc.pluginInfo('objExport', query=True, loaded=True)
    if export_type == 'OBJ' and not objExportPlugin:
        load_plugins = mc.loadPlugin('objExport')
        if load_plugins[0] != 'objExport':
            mc.warning('obj export plugin load failed')
            return -1
        else:
            print('Plugin loaded : obj export')
    export_info = {}
    if export_type == 'OBJ':
        export_info['typ'] = 'OBJexport'
        export_info['ext'] = 'obj'
        export_info['opt'] = \
            'group=0;ptgroups=0;materials=0;smoothing=1;normals=1'
    elif export_type == 'Maya Ascii':
        export_info['typ'] = 'mayaAscii'
        export_info['ext'] = 'ma'
        export_info['opt'] = 'v=0;'
    elif export_type == 'Maya Binary':
        export_info['typ'] = 'mayaBinary' 
        export_info['ext'] = 'mb'
        export_info['opt'] = 'v=0;'
    elif export_type == 'FBX':
        export_info['typ'] = 'fbx'
        export_info['ext'] = 'fbx'
        export_info['opt'] = ''
    else:
        mc.warning('Failed : Unknown export type : {0}'.format(export_type))
    pairs_mesh = {}
    if source == 0:
        pairs_mesh = _getPolygonFromDisplayLayers()
    elif source == 1:
        pairs_mesh = _getPolygonsFromSets()
    elif source == 2:
        selections = mc.ls(sl=True, l=True)
        if selections:
            pairs_mesh = {'export_mesh': selections}
        else:
            mc.warning('# Please select objects!')
            return -1
    #
    if not pairs_mesh:
        return -1
    if not _userConfirm('Export Meshes', '\n'.join(pairs_mesh.keys())):
        return -1
    store_selections = mc.ls(sl=True, l=True)
    amout = 0
    process_max = len(pairs_mesh)
    # Progress Window
    mc.progressWindow(title='Export Shaders', progress=amout,
        status='Export start...', isInterruptable=True, max=process_max)
    for key in pairs_mesh.keys():
        mc.select(cl=True)
        fullpath = '{0}/{1}.{2}'.format(export_path, key, export_info['ext'])
        for item in pairs_mesh[key]:
            shortName = item.split('|')[-1]
            if len(include) == 0 or shortName.find(include) >= 0 and \
            len(exclude) == 0 or shortName.find(exclude) == -1:
                mc.select(item, add=True)
        if len(mc.ls(sl=True)) == 0:
            continue
        try:
            mc.file(fullpath, f=True, exportSelected=True,
                type=export_info['typ'], options=export_info['opt'])
            amout += 1
            mc.progressWindow(e=True, progress=amout, 
                status='Export : {0} / {1}'.format(amout,  process_max))
        except:
            raise
        print('The meshes have been exported : '+fullpath)
    mc.progressWindow(endProgress = True)
    if objExportPlugin is not True:
        unloaded_plugins = mc.unloadPlugin('objExport')
        if unloaded_plugins[0] == 'objExport':
            print('Unload plug-in : objExport')
        else:
            mc.warning('Failed to unload plug-in : objExport')
    if store_selections:
        mc.select(store_selections, r=True)
    else:
        mc.select(cl=True)

def uvSnapshot(export_path, ext, res, colorSymbol, source=0):
    if not export_path:
        mc.warning('Please enter a output folder!')
        return -1
    if not isdir(export_path):
        mc.warning('The directory is invalid : {0}'.format(export_path))
        return -1
    pairs_mesh = {}
    # Get source 0: from display layer, 1:from sets, 2:from selected
    if source == 0:
        pairs_mesh = _getPolygonFromDisplayLayers()
    elif source == 1:
        pairs_mesh = _getPolygonsFromSets()
    elif source == 2:
        selections = mc.ls(sl=True, l=True)
        if selections:
            pairs_mesh = {'uv_snapshot': selections}
        else:
            mc.warning('# Please select objects!')
            return -1
    if not pairs_mesh:
        mc.warning('No any meshs can be snapshot')
        return -1
    if not _userConfirm('UV Snapshot', '\n'.join(pairs_mesh.keys())):
        return
    # Store previous selections
    store_selections = mc.ls(sl=True)
    amout = 0
    process_max = len(pairs_mesh)
    # UV Snapshot Color
    R, G, B = 0, 1, 2
    if colorSymbol == 'Black':
        color = (0, 0, 0)
    elif colorSymbol == 'White':
        color = (255, 255, 255)
    elif colorSymbol == 'Red':
        color = (255, 0, 0)
    else:
        color = (255, 255, 255)
    # Progress Window
    mc.progressWindow(title='UV Snapshot', progress=amout,
        status='Snapshot start...', isInterruptable=True, max=process_max)
    #
    for key in pairs_mesh.keys():
        mc.select(cl=True)
        fullpath = '{0}/{1}.{2}'.format(export_path, key , ext)
        try:
            mc.select(pairs_mesh[key], r=True)
            mc.uvSnapshot(overwrite=True,
                          redColor=color[R],
                          greenColor=color[G],
                          blueColor=color[B],
                          xResolution=int(res),
                          yResolution=int(res),
                          fileFormat=ext,
                          antiAliased=True,
                          name=fullpath)
            amout += 1
            mc.progressWindow(e=True,
                              progress=amout,
                              status='Snapshot : {0} / {1}'.format(
                              amout,  process_max))
        except:
            mc.progressWindow(endProgress=True)
            raise
        print('UV Snapshot > '+fullpath)
    # End the progress window
    mc.progressWindow(endProgress=True)
    if store_selections:
        mc.select(store_selections, r=True)
    else:
        mc.select(cl=True)

def createPhotoshopFile(export_path, uv_path, channels, res):
    if not export_path:
        mc.warning('# Please enter a output folder!')
        return -1
    if exists(export_path):
        mc.warning('# File is exists, Can not overwrite : '+export_path)
        return -1
    if not _userConfirm('Photoshop file', 'Create {0} ?'.format(export_path)):
        return -1
    command = 'psdTextureFile -uvt true -psf \"{0}\" '.format(export_path)
    command += '-xr {0} -yr {1} '.format(str(res), str(res))
    if isfile(uv_path):
        command += '-ssi \"{0}\" '.format(uv_path)
        print('# UV image found :' + uv_path)
    else:
        print('# UV image file was not found.')
    # Add layers flags
    channels_line = ''
    for idx, ch in enumerate(channels):
        #channels_line += '-chs {0} {1} {2} '.format(ch, str(idx), 'true')
        channels_line += '-chc {0} {1} 128 128 128 '.format(ch, str(idx))
    if channels_line:
        command += channels_line
    try:
        mel.eval(command)
    except:
        print command
        raise
    else:
        print '# Photoshop file create successiful! : ', export_path

def _userConfirm(title, message):
    ans = mc.confirmDialog(t=title, m=message, b=('Yes','No'), 
        db='Yes', cb='No', ds='No')
    if ans == 'Yes':
        return True
    return False

def _getPolygonFromDisplayLayers():
    visible_displaylayers = [ d for d in mc.ls(type='displayLayer')
        if mc.getAttr(d+'.visibility') and d not in ['defaultLayer']]
    if not visible_displaylayers:
        return {}
    polygonCollections = {}
    for dl in visible_displaylayers:
        itemsInLayer = mc.editDisplayLayerMembers(dl, q=True, fn=True)
        if not itemsInLayer:
            continue
        items = [o for o in itemsInLayer if mc.nodeType(o) in
            ['mesh', 'transform']]
        if not items:
            continue
        collections = []
        for item in items:
            if mc.nodeType(item) == 'mesh':
                collections.append(item)
            elif mc.nodeType(item) == 'transform':
                relatives = mc.listRelatives(item, ad=True,
                    type='mesh', ni=True, f=True)
                collections.extend(relatives)
        if collections:
            polygonCollections[dl] = collections
    return polygonCollections

def _getPolygonsFromSets():
    all_sets = [s for s in mc.ls(type='objectSet')
    if mc.nodeType(s) == 'objectSet' \
    and s not in ['defaultLightSet', 'defaultObjectSet']]
    if not all_sets:
        return {}
    polygonCollections = {}
    for se in all_sets:
        collections = []
        itemsInSet = [o for o in mc.sets(se, q=True) 
            if mc.nodeType(o) in ['mesh', 'transform']]
        if not itemsInSet:
            continue
        for item in itemsInSet:
            if mc.nodeType(item) == 'mesh':
                collections.append(item)
            elif mc.nodeType(item) == 'transform':
                relatives = mc.listRelatives(item, ad=True,
                    type='mesh', ni=True, f=True)
                collections.extend(relatives)
        if collections:
            polygonCollections[se] = collections
    return polygonCollections
