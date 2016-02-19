import sys
from os.path import exists
import string
import maya.cmds as mc
from config import kRelatives, kDegammaValue, kConnectSG
from config import kMayaVersion, kCurrentOS

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

def createShader(nlist, stype, cnames, checks, options, filters, rules):
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

        # If gamma correct is on, and this texture is scalar
        if gamma_correct_on and aAttr == 'outAlpha':
            if stype in [ 'blinn', 'mia_material_x_passes' ]:
                setColorSpace( filenode, kMayaVersion )

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

        # Here is deal with bump texture
        if idx == 1:
            if stype in ['blinn', 'mia_material_x_passes', 'aiStandard']:
                bump2d = mc.shadingNode( 'bump2d', \
                name = substituteVariables( bump2dRule, nlist ), asUtility = True )
                mc.connectAttr( filenode + '.' + aAttr, bump2d + '.bumpValue', f = True )
                mc.connectAttr( bump2d + '.outNormal', sname + '.' + bAttr, f = True )
                mc.setAttr( bump2d + '.bumpDepth', bump_value )
            elif stype in ['VRayMtl']:
                mc.connectAttr( filenode + '.' + aAttr, sname + '.' + bAttr, f = True )
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

def setColorSpace(filenode, version):
    if version in [ '2013', '2014' ]:
        mc.setAttr( filenode + '.colorProfile', 2 )
    elif version in [ '2015' ]:
        mc.setAttr( filenode + '.colorSpace', 'Raw', typ = 'string' )
    elif version in [ '2016' ]:
        pass
    else:
        pass
