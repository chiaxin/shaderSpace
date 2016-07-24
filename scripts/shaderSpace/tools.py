'''
Tools for shaderSpace Rapid Shader Workflow Tool in Maya
///////////////////////////////////////////////////////////
Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
E-Mail : nnnight@gmail.com
Github : http://github.com/chiaxin
'''
from os import listdir
from os.path import isfile, dirname, exists
import maya.cmds as mc
import maya.mel as mel

def exportShaders(export_path, mode):
    if not export_path:
        mc.warning('Please enter a output folder!')
        return
    if not exists(export_path):
        mc.warning('Directory is not exists :'+export_path)
        return
    shading_groups = []
    if mode == 'All':
        shading_groups = [s for s in mc.ls(type='shadingEngine')
            if s not in ('initialParticleSE', 'initialShadingGroup')]
    elif mode == 'Selected':
        selections = mc.ls(sl=True)
        if not selections:
            mc.warning(
                'Please select at least one shader or mesh, nurbsShapes.')
            return
        for sel in selections:
            connected_sg = mc.listConnections(sel, s=False,
                d=True, type='shadingEngine')
            if not connected_sg:
                continue
            shading_groups.extend([s for s in connected_sg
                if s not in ('initialParticleSE', 'initialShadingGroup')])
        shading_groups = list(set(shading_groups))
    else: 
        return
    if not shading_groups:
        mc.warning('There are no any shaders can be export!')
        return
    if not _userConfirm('Export Shaders', '\n'.join(shading_groups)):
        return
    connections = []
    fullpath = ''
    amout = 0
    process_max = len(shading_groups)
    mc.progressWindow(title='Export Shaders', progress=amout,
        status='Export start...', isInterruptable=True, max=process_max)
    for sg in shading_groups:
        if mc.progressWindow(q=True, isCancelled=True):
            break
        fullpath = '{0}{1}.ma'.format(export_path, sg)
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

def exportPolygons(export_path, export_type, exclude, include, group):
    if not export_path:
        mc.warning('Please enter a output folder!')
        return
    elif not exists(export_path):
        mc.warning('Directory is not exists : {0}'.format(export_path))
        return
    objExportPlugin = mc.pluginInfo('objExport', query=True, loaded=True)
    if export_type == 'obj' and not objExportPlugin:
        load_plugins = mc.loadPlugin('objExport')
        if load_plugins[0] != 'objExport':
            mc.warning('obj export plugin load failed')
            return
        else:
            print('Plugin loaded : obj export')
    export_info = {}
    if export_type == 'obj':
        export_info['typ'] = 'OBJexport'
        export_info['ext'] = 'obj'
        export_info['opt'] = \
            'group=0;ptgroups=0;materials=0;smoothing=1;normals=1'
    elif export_type == 'ma':
        export_info['typ'] = 'mayaAscii'
        export_info['ext'] = 'ma'
        export_info['opt'] = 'v=0;'
    elif export_type == 'mb':
        export_info['typ'] = 'mayaBinary' 
        export_info['ext'] = 'mb'
        export_info['opt'] = 'v=0;'
    else:
        mc.warning('Failed : Unknown export type : {0}'.format(export_type))
    pairs_mesh = {}
    if group == 0:
        pairs_mesh = _getPolygonFromDisplayLayers()
    elif group == 1:
        pairs_mesh = _getPolygonsFromSets()
    if not pairs_mesh:
        return
    if not _userConfirm('Export Meshes', '\n'.join(pairs_mesh.keys())):
        return 
    store_selections = mc.ls(sl=True)
    amout = 0
    process_max = len(pairs_mesh)
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

def uvSnapshot(export_path, ext, res, color, group):
    if not export_path:
        mc.warning('Please enter a output folder!')
        return
    if not exists(export_path):
        mc.warning('The directory is not exists : {0}'.format(export_path))
        return
    pairs_mesh = {}
    if group == 0:
        pairs_mesh = _getPolygonFromDisplayLayers()
    elif group == 1:
        pairs_mesh = _getPolygonsFromSets()
    if not pairs_mesh:
        mc.warning('No any meshs can be snapshot')
        return
    if not _userConfirm('UV Snapshot', '\n'.join(pairs_mesh.keys())):
        return
    store_selections = mc.ls(sl=True)
    amout = 0
    process_max = len(pairs_mesh)
    mc.progressWindow(title='UV Snapshot', progress=amout,
        status='Snapshot start...', isInterruptable=True, max=process_max)
    for key in pairs_mesh.keys():
        mc.select(cl=True)
        fullpath = '{0}/{1}.{2}'.format(export_path, key , ext)
        try:
            mc.select(pairs_mesh[key], r=True)
            mc.uvSnapshot(overwrite=True, \
                redColor=color[0], greenColor=color[1], blueColor=color[2],
                xResolution=int(res), yResolution=int(res), fileFormat=ext,
                name=fullpath)
            amout += 1
            mc.progressWindow(e=True, progress=amout, 
                status='Snapshot : {0} / {1}'.format(amout,  process_max))
        except:
            raise
        finally:
            mc.progressWindow(endProgress = True)
        print('UV Snapshot > '+fullpath)
    if store_selections:
        mc.select(store_selections, r=True)
    else:
        mc.select(cl=True)

def createPhotoshopFile(export_path, uv_path, channels, res):
    if not export_path:
        mc.warning('Please enter a output folder!')
        return
    if exists(export_path):
        mc.warning('File is exists, Can not overwrite it : '+export_path)
        return
    elif not exists(dirname(export_path)):
        mc.warning('Directory is not exists : {0}'.format(
            dirname(export_path)))
        return
    if not _userConfirm('Photoshop file', 'Create {0} ?'.format(export_path)):
        return
    execution = 'psdTextureFile -uvt true -psf \"{0}\" '.format(export_path)
    execution += '-xr {0} -yr {1} '.format(str(res), str(res))
    if isfile(uv_path):
        execution += '-ssi \"{0}\" '.format(uv_path)
        print('UV image found :' + uv_path)
    else:
        print('UV image file was not found.')
    channels_line = ''
    for idx, ch in enumerate(channels):
        channels_line += '-chs {0} {1} {2} '.format(ch, str(idx), 'false')
    if channels_line:
        execution += channels_line
    try:
        mel.eval(execution)
    except:
        raise

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
