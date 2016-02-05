from os import listdir
from os.path import isfile, join
from os.path import exists, join
from os.path import dirname, join
import maya.cmds as mc
import maya.mel as mel

def exportShaders(export_path, mode):
    if not export_path:
        mc.warning( 'Please enter a output folder!' )
        return
    if exists( export_path ) is not True:
        mc.warning( 'Directory is not exists :' + export_path )
        return
    shading_groups = []

    if mode == 'all':
        shading_groups = [ s for s in mc.ls(type='shadingEngine') \
        if s not in ['initialParticleSE', 'initialShadingGroup'] ]
    elif mode == 'selected':
        selections = mc.ls( sl = True )
        if not selections:
            mc.warning('Please select at least one shader or mesh, nurbsShapes.')
            return
        for sel in selections:
            connected_sg = mc.listConnections( sel, s = False, d = True, type = 'shadingEngine' )
            if not connected_sg:
                continue
            shading_groups.extend( [ s for s in connected_sg \
            if s not in ['initialParticleSE', 'initialShadingGroup'] ] )
        shading_groups = list( set(shading_groups) )
    else: return
    if not shading_groups:
        mc.warning('There are no any shaders can be export!')
        return
    ans = mc.confirmDialog( t = 'Export Shaders', m = '\n'.join( shading_groups ), \
    button=['Yes','No'], db = 'Yes', cb = 'No', ds = 'No' )
    if ans == 'No': return

    connections = []
    fullpath = ''
    for sg in shading_groups:
        fullpath = '{0}/{1}.ma'.format( export_path, sg )
        connections = mc.listHistory( sg, allFuture=True, pruneDagObjects=True )
        mc.select( connections, replace = True, noExpand = True )
        try:
            mc.file( fullpath, force = True, exportSelected = True, type = 'mayaAscii', options = 'v=0;' )
        except:
            raise
        mc.select( cl = True )
        print('Export : {0} > {1}'.format( sg, fullpath ) )

def exportPolygons(export_path, export_type, exclude, include):
    if not export_path:
        mc.warning( 'Please enter a output folder!' )
        return
    elif not exists(export_path):
        mc.warning( 'Directory is not exists : {0}'.format( export_path ) )
        return

    objExportPlug = mc.pluginInfo('objExport', query=True, loaded=True)

    if export_type == 'obj' and not objExportPlug:
        load_plugins = mc.loadPlugin('objExport')
        if load_plugin[0] != 'objExport':
            mc.warning('obj export plugin load failed')
            return
        else:
            print('Plugin loaded : obj export')

    export_info = {}
    if export_type == 'obj':
        export_info['typ'] = 'OBJexport'
        export_info['ext'] = 'obj'
        export_info['opt'] = 'group=0;ptgroups=0;materials=0;smoothing=1;normals=1'
    elif export_type == 'ma':
        export_info['typ'] = 'mayaAscii'
        export_info['ext'] = 'ma'
        export_info['opt'] = 'v=0;'
    elif export_type == 'mb':
        export_info['typ'] = 'mayaBinary' 
        export_info['ext'] = 'mb'
        export_info['opt'] = 'v=0;'
    else:
        mc.warning( 'Failed : Unknown export type : {0}'.format( export_type ) )

    visible_displaylayers = [ d for d in mc.ls( type = 'displayLayer' ) \
    if mc.getAttr( d + '.visibility' ) ]
    visible_displaylayers.remove('defaultLayer')

    if len(visible_displaylayers) == 0:
        mc.warning('Not any visible display layer was found')
        return

    ans = mc.confirmDialog( t = 'Export Meshes', m = '\n'.join( visible_displaylayers ), \
    button=['Yes','No'], db = 'Yes', cb = 'No', ds = 'No' )
    if ans == 'No':
        return

    store_selections = mc.ls( sl = True )
    for dl in visible_displaylayers:
        itemsInLayer = mc.editDisplayLayerMembers( dl, q = True, fn = True )
        if itemsInLayer is None:
            mc.warning( 'Display-layer empty : {0}'.format( dl ) )
            continue
        mc.select( cl = True )
        fullpath = '{0}/{1}.{2}'.format( export_path, dl, export_info['ext'] )
        for under in itemsInLayer:
            if mc.nodeType( under ) not in [ 'mesh', 'transform' ]:
                continue
            short = under.split('|')[-1]
            if short.find( include ) >= 0 and short.find( exclude ) < 0:
                mc.select( under, add = True )
        if len( mc.ls( sl = True ) ) == 0:
            continue
        try:
            mc.file( fullpath, f = True, exportSelected = True,
            type = export_info['typ'], options = export_info['opt'] )
        except:
            raise
        print( 'The meshes have been exported : ' + fullpath )

    if objExportPlug is not True:
        unloaded_plugins = mc.unloadPlugin('objExport')
        if unloaded_plugins[0] == 'objExport':
            print('Unload plug-in : objExport')
        else:
            mc.warning('Failed to unload plug-in : objExport')
    if store_selections:
        mc.select( store_selections, r = True )

def uvSnapshot(export_path, res, ext, color):
    if not export_path:
        mc.warning( 'Please enter a output folder!' )
        return
    if not exists(export_path):
        mc.warning( 'The directory is not exists : {0}'.format(export_path) )
        return
    visible_displaylayers = [ d for d in mc.ls(type='displayLayer') \
    if mc.getAttr( d + '.visibility' ) ]

    visible_displaylayers.remove('defaultLayer')

    if not visible_displaylayers:
        mc.warning('Not any visible display-layers found')
        return

    ans = mc.confirmDialog( t = 'UV Snapshot', m = '\n'.join( visible_displaylayers ), \
    button=['Yes','No'], db = 'Yes', cb = 'No', ds = 'No' )
    if ans == 'No':
        return
    store_selections = mc.ls(sl=True)

    for dl in visible_displaylayers:
        mc.select( cl = True )
        fullpath = '{0}/{1}.{2}'.format( export_path, dl, ext )
        itemsInLayer = mc.editDisplayLayerMembers( dl, q = True, fn = True )
        if itemsInLayer is None:
            mc.warning( 'Display-layer empty : {0}'.format( dl ) )
            continue
        items = [ o for o in itemsInLayer if mc.nodeType( o ) in [ 'mesh', 'transform' ] ]
        if not items:
            mc.warning( 'This display-layer has no any vaild mesh : {0}'.format(dl) )
            continue
        try:
            mc.select( items, r = True )
            mc.uvSnapshot(overwrite=True, \
            redColor = color[0], greenColor = color[1], blueColor = color[2], \
            xResolution = res, yResolution = res, fileFormat = ext, name = fullpath )
        except:
            raise
        print('UV Snapshot > ' + fullpath)
    if store_selections:
        mc.select( store_selections, r = True )

def createPhotoshopFile(export_path, uv_path, channels, res):
    if not export_path:
        mc.warning( 'Please enter a output folder!' )
        return
    if exists(export_path):
        mc.warning( 'File is exists, Can not overwrite it : ' + export_path )
        return
    elif not exists( dirname( export_path ) ):
        mc.warning('Directory is not exists : {0}'.format( dirname( export_path ) ) )
        return
    ans = mc.confirmDialog( t = 'Create Photoshop file', m = 'Create {0} ?'.format(export_path), \
    button=['Yes','No'], db = 'Yes', cb = 'No', ds = 'No' )
    if ans == 'No': return

    execution = 'psdTextureFile -uvt true -psf \"{0}\" '.format( export_path )
    execution += '-xr {0} -yr {1} '.format( str( res ), str( res ) )

    if exists(uv_path):
        execution += '-ssi \"{0}\" '.format( uv_path )
        print( 'UV image found :' + uv_path )
    else:
        print( 'UV image file was not found.' )
    channels_line = ''
    for idx, ch in enumerate( channels ):
        channels_line += '-chs {0} {1} {2} '.format( ch, str(idx), 'false' )
    if channels_line:
        execution += channels_line
    try:
        mel.eval( execution )
    except:
        raise
