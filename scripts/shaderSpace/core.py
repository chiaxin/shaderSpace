'''
    Core Functions for shaderSpace Rapid Shader Workflow Tool in Maya

    Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
    E-Mail : nnnight@gmail.com
    Github : http://github.com/chiaxin
'''
import sys
import os.path
import string
from functools import partial

from config import kShadersList, kRelatives, kDegammaValue, kConnectSG
from config import kBumpChannel, kShaderPlugins
from config import kMayaVersion, kCurrentOS
from config import kColorManagementShaders, kLinearProfile, kVrayColorMangementShaders
from config import kVrayDegammaMethod, kVrayDegammaValue

import maya.cmds as mc
import maya.mel as mel

class LogUI:
    Win = 'shaderSpaceLogWin'
    Con = 'shaderSpaceLogCon'
    Title = 'Log'
    WidthHeight = (360, 480)
    def __init__(self):
        pass

    def build(self):
        self.destroy()
        self.Win = mc.window(self.Win, wh=self.WidthHeight, title=self.Title)
        mc.columnLayout(cat=('both', 20), cw=8, adj=True)
        self.Con = mc.scrollField(self.Con, editable=False, wordWrap=False, \
        h=420, font='fixedWidthFont', text='--- Shader Process Log ---\n')
        mc.button(h=36, l='Confirm', c=lambda x: mc.deleteUI(self.Win))
        mc.setParent('..')

    def destroy(self):
        if mc.window(self.Win, q=True, ex=True):
            mc.deleteUI(self.Win)

    def show(self):
        mc.showWindow(self.Win)
        mc.window(self.Win, e=True, wh=self.WidthHeight)

    def append(self, *args):
        for line in args:
            mc.scrollField(self.Con, e=True, ip=0, it=line + '\n')

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

def substituteVariables(rule, **kwargs):
    # kwargs: asset, shader, user, version, channel
    if not rule:
        return ''
    # There get variable keywords and replace.
    rule = rule.replace('<asset>',  kwargs.get('asset', 'asset'))
    rule = rule.replace('<shader>', kwargs.get('shader', 'shader'))
    rule = rule.replace('<user>',   kwargs.get('user', 'user'))
    rule = rule.replace('<version>',kwargs.get('version', 'version'))
    rule = rule.replace('<root>',  mc.workspace(q=True, rootDirectory=True))
    # If channel is filled, replace it
    if kwargs.has_key('channel'):
        rule = rule.replace('<channel>', kwargs.get('channel', ''))
    # Determine camel case format
    buffer = rule.split('<c>')
    for idx in range(len(buffer)-1):
        if buffer[idx][-1].islower():
            buffer[idx+1] = buffer[idx+1][0].upper() + buffer[idx+1][1:]
        elif buffer[idx][-1].isupper():
            buffer[idx+1] = buffer[idx+1][0].lower() + buffer[idx+1][1:]
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
    p2d = mc.shadingNode( 'place2dTexture', name=mainname, asUtility = True )
    mc.setAttr(p2d + '.mirrorU', mirrorU)
    mc.setAttr(p2d + '.mirrorV', mirrorV)
    return p2d

def isExistsNodeType(typ):
    return (typ in mc.ls(nodeTypes=True))

def createShader(*args, **kwargs):
    try:
        shaderType  = kwargs['shaderType']
        preset      = kwargs['preset']
        cnames      = kwargs['channelNames']
        checks      = kwargs['checks']
        filters     = kwargs['filters']
        autoPathRule= kwargs['autopathRule']
        shaderRule  = kwargs['shaderRule']
        shadingRule = kwargs['shadingGroupRule']
        textureRule = kwargs['textureRule']
        bump2dRule  = kwargs['bump2dRule']
        place2dRule = kwargs['place2dTextureRule']
        matinfoRule = kwargs['materialInfoRule']
        isAutopath  = kwargs['isAutopath']
        isUvMirror  = kwargs['isUvMirror']
        bumpValue   = kwargs['bumpValue']
        showLog     = kwargs['showLog']
        isGammaCorrect = kwargs['isGammaCorrect']
        isAlphaIsLum = kwargs['isAlphaIsLum']
        isSharedPlace2dTexture = kwargs['isSharedP2d']
        isIgnoreTextureIsNotExists = kwargs['igroneTexIsNotExists']
    except:
        mc.warning('Failed to get options in create shader function')
        raise
    substituteWordFunc = partial(substituteVariables, \
    asset=kwargs.get('asset', 'asset'), user=kwargs.get('user', 'user'), \
    shader=kwargs.get('shader', 'shader'), version=kwargs.get('version', 'version'))
    if not isExistsNodeType(shaderType):
        mc.error('Unknown type : {0}'.format(shaderType))
        return
    mainShader = substituteWordFunc(shaderRule)

    # Shader name is invaild?
    if not isVaildName(mainShader):
        mc.warning('Shader name is invaild : ' + mainShader)
        return
    # Is shader exists? if so, ask user.
    if mc.objExists(mainShader) and mc.confirmDialog(\
    t='Exists', m='Shader is exists, continue?', button=['Yes', 'No'],\
    db='Yes', cb='No', ds='No') == 'No': return

    # Log window build
    logUi = LogUI(); logUi.build()

    # Shader create
    mainShader = mc.shadingNode(shaderType, name=mainShader, asShader=True)
    logUi.append('>> Shader Create :\n', mainShader)

    # Preset, using source command
    if preset:
        presetPath = '{0}attrPresets/{1}/{2}.mel'.format(mc.internalVar(ups=True), shaderType, preset)
        if os.path.isfile(presetPath):
            mel.eval('source \"{0}\"'.format(presetPath))
            logUi.append('>> Preset Set - \n{0}\n'.format(preset))
        else:
            mc.warning('Preset mel not found : {1}'.format(presetPath))

    # Shading Group create
    shadingGroup = mc.sets(renderable=True, noSurfaceShader=True, \
    empty=True, name=substituteWordFunc(shadingRule))
    logUi.append('>> ShadingEngine Create - \n{0}\n'.format(shadingGroup))

    # Rename material info
    materialInfo = mc.listConnections(shadingGroup, s=False, d=True, type='materialInfo')[0]
    materialInfo = mc.rename(materialInfo, substituteWordFunc(matinfoRule))
    logUi.append('>> materialInfo Rename - \n{0}\n'.format(materialInfo))

    # Get connection pair
    connectTable = kRelatives[shaderType]
    connectSgTable = kConnectSG[shaderType]

    # Connect shader to shading group
    for pair in connectSgTable:
        #print '{0} connect to {1}'.format( pair[0], pair[1] )
        mc.connectAttr(mainShader + '.' + pair[0], shadingGroup + '.' + pair[1])

    # Create and connect each channels
    newTextureList = []
    newTextureChannels = []
    for idx, pairs in enumerate(connectTable):
        if not checks[idx]:
            continue

        # Texture node create
        filenode = mc.shadingNode('file', \
        name=substituteWordFunc(textureRule, channel=cnames[idx]), asTexture=True)
        logUi.append('>> Texture Create - \n{0}\n'.format(filenode))

        # aAttr is output attribute from texture, bAttr is input attribute into shader
        aAttr = pairs[0]
        bAttr = pairs[1]

        # This texture is a color map?
        isColorChannel = (aAttr == 'outColor')

        # Exclude bump map in VRay, because Bump map in VRay is outColor way.
        if shaderType in kVrayColorMangementShaders and bAttr == 'bumpMap':
            isColorChannel = False

        # Gamma correct setting :
        # In maya built-in shader or MentalRay, we need to set linear profile if is not color channel.
        # In VRay, we need to add VRay degamma attribute, and set it to sRGB if is color channel.
        if isGammaCorrect:
            if shaderType in kColorManagementShaders and not isColorChannel:
                setColorSpaceToLinear(filenode, kMayaVersion)
                logUi.append('>> Color-Profile to Linear - \n{0}\n'.format(filenode))
            elif shaderType in kVrayColorMangementShaders and isColorChannel:
                setVrayColorSpace(filenode, kVrayDegammaMethod, kVrayDegammaValue)
                logUi.append('>> Color-Profile to sRGB - \n{0}\n'.format(filenode))

        # If auto file path is on
        if isAutopath:
            fileTextureName = substituteWordFunc(autoPathRule, channel=cnames[idx])
            if isIgnoreTextureIsNotExists and not os.path.isfile(fileTextureName):
                logUi.append('>> Not Exists - \n{0}\n'.format(fileTextureName))
            else:
                mc.setAttr(filenode + '.fileTextureName', fileTextureName, type='string')
                logUi.append('>> Path Assign - \n{0}\n'.format(fileTextureName))

        # If this texture is scalar
        if aAttr == 'outAlpha' and isAlphaIsLum:
            mc.setAttr(filenode + '.alphaIsLuminance', 1)
            logUi.append('>> Alpha Is Luminance On - \n{0}\n'.format(filenode))

        # Set file's filter
        mc.setAttr(filenode + '.filterType', filters[idx])
        logUi.append('>> Set Filter Type - \n{0}, {1}\n'.format(filenode, filters[idx]))

        # Here is deal with bump texture, index(9)
        if idx == 9:
            # if shaderType in ['blinn', 'mia_material_x_passes', 'aiStandard']:
            if kBumpChannel[shaderType] == 'bump2d':
                bump2d = mc.shadingNode('bump2d', name=substituteWordFunc(bump2dRule), asUtility=True)
                logUi.append('>> Bump Build - \n{0}\n'.format(bump2d))
                mc.connectAttr(filenode + '.' + aAttr, bump2d + '.bumpValue', f=True)
                mc.connectAttr(bump2d + '.outNormal', mainShader + '.' + bAttr, f=True)
                mc.setAttr(bump2d + '.bumpDepth', bumpValue)
            # else if shaderType in ['VRayMtl']:
            elif kBumpChannel[shaderType] == 'file':
                mc.connectAttr(filenode + '.' + aAttr, mainShader + '.' + bAttr, f=True)
                logUi.append('>> Bump Connect')
                if shaderType == 'VRayMtl':
                    mc.setAttr(mainShader + '.bumpMult', bumpValue)
            logUi.append('>> Bump Value - \n{0}\n'.format(bumpValue))
        else:
            mc.connectAttr(filenode + '.' + aAttr, mainShader + '.' + bAttr)
            logUi.append('>> Connect - \n{0}.{1} to {2}.{3}\n'.format(filenode, aAttr, mainShader, bAttr))
        newTextureList.append(filenode)
        newTextureChannels.append(cnames[idx])

    # Otherwise, We need to create place2dTexture for each map.
    uvMirror = [0, 0]
    uvMirrorMethods = ((1,0), (0,1), (1,1))
    if isUvMirror >= 0:
        uvMirror = uvMirrorMethods[isUvMirror]

    # If Shared Place2dTexture is on, we create a place2dTexture node connect to each map.
    place2dTextureNodeName = substituteWordFunc(place2dRule)
    if isSharedPlace2dTexture and newTextureList:
        p2d = buildPlace2dTexture(place2dTextureNodeName, uvMirror[0], uvMirror[1])
        for f in newTextureList:
            connectPlace2dTexture(f, p2d)
        logUi.append('>> Shared Place2dTexture - \n{0}\n'.format(p2d))
    else:
        for idx, f in enumerate(newTextureList):
            if place2dRule.find('<channel>') == -1:
                p2d = buildPlace2dTexture(\
                place2dTextureNodeName + '_' + chr(idx+65), uvMirror[0], uvMirror[1])
            else:
                place2dTextureNodeName = substituteWordFunc(\
                place2dRule, channel=newTextureChannels[idx])
                p2d = buildPlace2dTexture(place2dTextureNodeName, uvMirror[0], uvMirror[1])
            connectPlace2dTexture(f, p2d)
            logUi.append('>> Place2dTexture - \n{0}\n'.format(p2d))

    if showLog: logUi.show()
    else: logUi.destroy()
    return mainShader, shadingGroup

def setColorSpaceToLinear(filenode, version):
    if version in [ '2014' ]:
        # 0: Use Default Input Profile, 2: Linear sRGB, 3: sRGB
        mc.setAttr( filenode + '.colorProfile', 2 )
    elif version in [ '2015' ]:
        if kLinearProfile in mc.colorManagementCatalog( ltc = True, type = 'input' ):
            mc.setAttr( filenode + '.colorSpace', kLinearProfile, typ = 'string' )
        else:
            mc.warning( 'The {0} is not in color transforms'.format( kLinearProfile ) )
    elif version in [ '2016' ]:
        # Not yet implement
        pass
    else:
        pass

def setVrayColorSpace(filenode, colorspace, gamma):
    try:
        mel.eval('vray addAttributesFromGroup ' + filenode + ' vray_file_gamma 1;')
        mc.setAttr(filenode + '.vrayFileGammaEnable', True)
        mc.setAttr(filenode + '.vrayFileColorSpace', colorspace)
        mc.setAttr(filenode + '.vrayFileGammaValue', gamma)
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
