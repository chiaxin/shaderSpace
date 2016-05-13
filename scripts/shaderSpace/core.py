import sys
from os.path import exists
import string
import maya.cmds as mc
import maya.mel as mel
from config import kShadersList, kRelatives, kDegammaValue, kConnectSG
from config import kBumpChannel, kShaderPlugins
from config import kMayaVersion, kCurrentOS
from config import kColorManagementShaders, kLinearProfile, kVrayColorMangementShaders

def isVaildName(name):
    if not name:
        return False
    elif name[0] in string.digits:
        return False
    for n in name[1:]:
        if n == '_':
            continue
        elif n in string.ascii_letters:
            continue
        elif n in string.digits:
            continue
        else:
            return False
    return True

def substituteVariables(rule, name_list, channel=''):
    if not rule:
        return ''
    # Get variable from text field
    asset = name_list[0]
    shade = name_list[1]
    user  = name_list[2]
    vers  = name_list[3]
    root = mc.workspace( q = True, rootDirectory=True )
    # Replace every variabeles
    rule = rule.replace( '<asset>', asset )
    rule = rule.replace( '<shader>', shade )
    rule = rule.replace( '<user>', user )
    rule = rule.replace( '<version>', vers )
    rule = rule.replace( '<root>',  root )
    # If channel is filled, replace it
    if channel != '':
        rule = rule.replace('<channel>', channel)
    # Determine camel case format
    buffer = rule.split('<c>')
    for idx in range(len(buffer)-1):
        if buffer[idx][-1] in string.lowercase[0:]:
            buffer[idx+1] = buffer[idx+1][:1].upper() + buffer[idx+1][1:]
        elif buffer[idx][-1] in string.uppercase[0:]:
            buffer[idx+1] = buffer[idx+1][:1].lower() + buffer[idx+1][1:]
    return ''.join(buffer).replace('\\', '/')

def connectPlace2dTexture(fileNode, p2dNode):
    if mc.nodeType(fileNode) != 'file':
        raise ValueError( fileNode + ' is not a file node!' )
    elif mc.nodeType(p2dNode) != 'place2dTexture':
        raise ValueError( p2dNode + ' is not a place2dTexture node!' )
    pairs = (\
    ('coverage', 'coverage'), ('translateFrame', 'translateFrame'),\
    ('rotateFrame', 'rotateFrame'), ('mirrorU', 'mirrorU'),\
    ('mirrorV', 'mirrorV'), ('stagger', 'stagger'),\
    ('wrapU', 'wrapU'), ('wrapV', 'wrapV'),\
    ('repeatUV', 'repeatUV'), ('offset', 'offset'),\
    ('rotateUV', 'rotateUV'), ('noiseUV', 'noiseUV'),\
    ('vertexUvOne', 'vertexUvOne'), ('vertexUvTwo', 'vertexUvTwo'),\
    ('vertexUvThree', 'vertexUvThree'), ('vertexCameraOne', 'vertexCameraOne'),\
    ('outUV', 'uv'), ('outUvFilterSize', 'uvFilterSize'))
    for attr in pairs:
        mc.connectAttr( ( p2dNode + '.' + attr[0] ), ( fileNode + '.' + attr[1] ), force=True)

def buildPlace2dTexture(mainname, mirrorU, mirrorV):
    p2d = mc.shadingNode( 'place2dTexture', name = mainname + '_place2dTexture', asUtility = True )
    mc.setAttr( p2d + '.mirrorU', mirrorU )
    mc.setAttr( p2d + '.mirrorV', mirrorV )
    return p2d

def isExistsNodeType(typ):
    return ( typ in mc.ls( nodeTypes = True ) )

def createShader(nlist, stype, cnames, checks, options, filters, rules, preset):
    if not isExistsNodeType( stype ):
        mc.error( 'Unknown type : {0}'.format( stype ) )
        return
    try:
        autoPathRule= rules['APR']
        shaderRule  = rules['SNR']
        shadingRule = rules['SGN']
        textureRule = rules['TEX']
        bump2dRule  = rules['B2D']
        place2dRule = rules['P2D']
        matinfoRule = rules['MIF']
        assign_selected = options[0]
        gamma_correct_on= options[1]
        autopath_on     = options[2]
        mirror_tex      = options[3]
        bump_value      = options[4]
        ignore          = options[5]
        alpha_is_lum    = options[6]
    except:
        sys.stderr.write( 'Failed to get options in create shader function' )
        raise

    sname = substituteVariables( shaderRule, nlist )

    if not isVaildName( sname ):
        mc.warning('Shader name is invaild : ' + sname )
        return
    if mc.objExists( sname ):
        ans = mc.confirmDialog( t = 'Exists', m = 'Shader is exists, continue?', \
        button=['Yes','No'], db = 'Yes', cb = 'No', ds = 'No' )
        if ans == 'No':
            return
    # Shader create
    sname = mc.shadingNode( stype, name = sname, asShader = True )

    # Preset, using source command
    if preset:
        presetPath = '{0}attrPresets/{1}/{2}.mel'.format( mc.internalVar( ups = True ), stype, preset )
        if exists(presetPath):
            mel.eval('source "{0}"'.format(presetPath))
        else:
            mc.warning( 'Preset mel not found : {1}'.format( presetPath ) )

    # Shading Group create
    sengine = mc.sets( renderable = True, noSurfaceShader = True, empty = True, \
    name = substituteVariables( shadingRule, nlist ) )

    # Rename material info
    material_info = mc.listConnections( sengine, s = False, d = True, type = 'materialInfo' )[0]
    material_info = mc.rename( material_info, substituteVariables( matinfoRule, nlist ) )

    # Get connection pair
    connect_table = kRelatives[stype]
    connect_sg = kConnectSG[stype]

    # Connect shader to shading group
    for pair in connect_sg:
        print '{0} connect to {1}'.format( pair[0], pair[1] )
        mc.connectAttr( sname + '.' + pair[0], sengine + '.' + pair[1] )

    # Create and connect each channels
    newTextureList = []
    for idx, pairs in enumerate( connect_table ):
        if not checks[idx]:
            continue

        filenode = mc.shadingNode( 'file', \
        name = substituteVariables( textureRule, nlist, cnames[idx] ), asTexture = True )

        aAttr = pairs[0]
        bAttr = pairs[1]

        isColorChannel = ( aAttr == 'outColor' )

        # Exclude bump map in VRay, because Bump map in VRay is outColor way.
        if stype in kVrayColorMangementShaders and bAttr == 'bumpMap':
            isColorChannel = False

        # Gamma correct setting :
        # In maya built-in shader or MentalRay, we need to set linear profile if is not color channel.
        # In VRay, we need to add VRay degamma attribute, and set it to sRGB if is color channel.
        if stype in kColorManagementShaders and not isColorChannel:
            setColorSpaceToLinear( filenode, kMayaVersion )
        elif stype in kVrayColorMangementShaders and isColorChannel:
            try:
                setVrayTextureDegamma( filenode )
            except ValueError as detail:
                mc.error( detail )
            except:
                raise

        # If auto file path is on
        if autopath_on:
            file_path = substituteVariables( autoPathRule, nlist, cnames[idx] )
            if ignore:
                if exists( file_path ):
                    mc.setAttr( filenode + '.fileTextureName', file_path, type = 'string' )
                else:
                    print '{0} is not exists. skip.'.format( file_path )
            else:
                mc.setAttr( filenode + '.fileTextureName', file_path, type = 'string' )

        # If this texture is scalar
        if aAttr == 'outAlpha' and alpha_is_lum:
            mc.setAttr( filenode + '.alphaIsLuminance', 1 )

        # Set file's filter
        mc.setAttr( filenode + '.filterType', filters[idx] )

        # Here is deal with bump texture, index(9)
        if idx == 9:
            #if stype in ['blinn', 'mia_material_x_passes', 'aiStandard']:
            if kBumpChannel[ stype ] == 'bump2d':
                bump2d = mc.shadingNode( 'bump2d', \
                name = substituteVariables( bump2dRule, nlist ), asUtility = True )
                mc.connectAttr( filenode + '.' + aAttr, bump2d + '.bumpValue', f = True )
                mc.connectAttr( bump2d + '.outNormal', sname + '.' + bAttr, f = True )
                mc.setAttr( bump2d + '.bumpDepth', bump_value )
            #elif stype in ['VRayMtl']:
            elif kBumpChannel[ stype ] == 'file':
                mc.connectAttr( filenode + '.' + aAttr, sname + '.' + bAttr, f = True )
                if stype == 'VRayMtl':
                    mc.setAttr( sname + '.bumpMult', bump_value )
        else:
            mc.connectAttr( filenode + '.' + aAttr, sname + '.' + bAttr )
        newTextureList.append( filenode )

    if len( newTextureList ) != 0:
        if mirror_tex == -1:
            p2d = buildPlace2dTexture( substituteVariables( place2dRule, nlist ), 0, 0)
        elif mirror_tex == 0:
            p2d = buildPlace2dTexture( substituteVariables( place2dRule, nlist ), 1, 0)
        elif mirror_tex == 1:
            p2d = buildPlace2dTexture( substituteVariables( place2dRule, nlist ), 0, 1)
        elif mirror_tex == 2:
            p2d = buildPlace2dTexture( substituteVariables( place2dRule, nlist ), 1, 1)
        for f in newTextureList:
            connectPlace2dTexture( f, p2d )
        mc.rename( p2d, substituteVariables( place2dRule, nlist ) )

    if assign_selected:
        selections = mc.ls( sl = True, type = [ 'mesh', 'transform', 'nurbsSurface' ] )
        if selections:
            print selections
    return sname, sengine

def setColorSpaceToLinear(filenode, version):
    if version in [ '2014' ]:
        mc.setAttr( filenode + '.colorProfile', 2 )
    elif version in [ '2015' ]:
        if kLinearProfile in mc.colorManagementCatalog( ltc = True, type = 'input' ):
            mc.setAttr( filenode + '.colorSpace', kLinearProfile, typ = 'string' )
        else:
            mc.warning( 'The {0} is not in color transforms'.format( kLinearProfile ) )
    elif version in [ '2016' ]:
        pass
    else:
        pass

def setVrayTextureDegamma(filenode):
    if not mc.objExists( filenode ):
        raise ValueError( 'The {0} is not exists!'.filenode )
    elif not mc.nodeType( filenode ):
        raise ValueError( 'The {0} is not file node!'.filenode )
    try:
        mel.eval('vray addAttributesFromGroup ' + filenode + ' vray_file_gamma 1;')
        mc.setAttr( filenode + '.vrayFileGammaEnable', True )
        # color space - 0: linear, 1: Gamma, 2: sRGB
        mc.setAttr( filenode + '.vrayFileColorSpace', 2 )
    except:
        raise

def reconnectShader(source, material):
    current_type = mc.nodeType( source )
    need_plugin = kShaderPlugins[material]
    if current_type not in kShadersList or material not in kShadersList:
        raise ValueError('Failed because shader is invaild')
    if mc.nodeType(source) == material:
        raise ValueError('Failed because they are same type')
    if not mc.pluginInfo( need_plugin, q = True, loaded = True ) and need_plugin != 'none':
        raise ValueError('Please load plug-in : {0}'.format( kShaderPlugins[material] ))

    # Build new shader and shading Group
    shader = source + '_rebuild'
    shadingGroup = source + '_rebuild_SG'
    shader = mc.shadingNode( material, name = shader, asShader = True )
    shadingGroup = mc.sets( renderable = True, noSurfaceShader = True, empty = True, \
    name = shadingGroup )

    connectsg_pair = kConnectSG[ material ]
    for pair in connectsg_pair:
        mc.connectAttr(  shader + '.' + pair[0], shadingGroup + '.' + pair[1], f = True )

    source_connections = kRelatives[ current_type ]
    target_connections = kRelatives[ material ]
    for idx, attribute in enumerate(target_connections):
        if idx == 9:
            if kBumpChannel[ material ] == 'bump2d':
                bump2d = mc.listConnections( source + '.' + source_connections[idx][1], s = True, d = False, type = 'bump2d' )
                if bump2d:
                    mc.connectAttr( bump2d[0] + '.outNormal', shader + '.' + attribute[1], f = True )
                else:
                    connected_files = mc.listConnections( source + '.' + source_connections[idx][1], s = True, d = True, type = 'file' )
                    if connected_files:
                        rebuild_bump2d = mc.shadingNode( 'bump2d', name = source + '_rebuild_bump2d', asUtility = True )
                        mc.connectAttr( connected_files[0] + '.' + attribute[0], rebuild_bump2d + '.bumpValue', f = True )
                        mc.connectAttr( rebuild_bump2d + '.outNormal', shader + '.' + attribute[1] )
            elif kBumpChannel[ material ] == 'file':
                connections = mc.listConnections( source + '.' + source_connections[idx][1], s = True, d = False )
                if mc.nodeType( connections[0] ) == 'bump2d':
                    connected = mc.listConnections( connections[0] + '.bumpValue', s = True, d = False )
                    if connected:
                        mc.connectAttr( connected[0] + '.' + attribute[0], shader + '.' + attribute[1], f = True )
                elif mc.nodeType( connections[0] ) == 'file':
                    mc.connectAttr( connections[0] + '.' + attrubute[0], shader + '.' + attribute[1], f = True )
        else:
            connections = mc.listConnections( source + '.' + source_connections[idx][1], s = True, d = False )
            if not connections:
                continue
            if mc.attributeQuery( attribute[0], node = connections[0], exists = True ):
                mc.connectAttr( connections[0] + '.' + attribute[0], shader + '.' + attribute[1], f = True )
            else:
                mc.warning( '{0} not has attribue : {1}, ignore.'.format( connections[0], attribute[0] ) )
    return shader, shadingGroup
