'''
Core for shaderSpace Rapid Shader Workflow Tool in Maya

Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
E-Mail : nnnight@gmail.com
Github : http://github.com/chiaxin
'''
import re
import sys
import os.path
from functools import partial
import maya.cmds as mc
import maya.mel as mel
from config import *

def isVaildName(name):
    matcher = re.match(r'[a-zA-Z_]\w+', name)
    if matcher:
        return True
    return False

def _substituteVariables(rule, **kwargs):
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

def _connectToPlace2dTexture(fileNode, p2dNode):
    pairs = (('coverage', 'coverage'),
             ('translateFrame', 'translateFrame'),
             ('rotateFrame', 'rotateFrame'),
             ('mirrorU', 'mirrorU'),
             ('mirrorV', 'mirrorV'),
             ('stagger', 'stagger'),
             ('wrapU', 'wrapU'),
             ('wrapV', 'wrapV'),
             ('repeatUV', 'repeatUV'),
             ('offset', 'offset'),
             ('rotateUV', 'rotateUV'),
             ('noiseUV', 'noiseUV'),
             ('vertexUvOne', 'vertexUvOne'),
             ('vertexUvTwo', 'vertexUvTwo'),
             ('vertexUvThree', 'vertexUvThree'),
             ('vertexCameraOne', 'vertexCameraOne'),
             ('outUV', 'uv'), 
             ('outUvFilterSize', 'uvFilterSize'))
    for attr in pairs:
        mc.connectAttr((p2dNode+'.'+attr[0]),
            (fileNode+'.'+attr[1]), force=True)

def _buildPlace2dTexture(mainname, mirrorU, mirrorV):
    p2d = mc.shadingNode('place2dTexture', name=mainname, asUtility=True)
    mc.setAttr(p2d+'.mirrorU', mirrorU)
    mc.setAttr(p2d+'.mirrorV', mirrorV)
    return p2d

def _isExistsNodeType(typ):
    return (typ in mc.ls(nodeTypes=True))

def createShader(*args, **kwargs):
    try:
        shaderType = kShadersList[kwargs['shaderSpaceShaderIntOptVar']]
        preset = kwargs['preset']
        cnames = kwargs['shaderSpaceAbbreviationsStrOptVars']
        checks = kwargs['shaderSpaceChannelsIntOptVars']
        filterTypeIdx = kwargs['shaderSpaceFilterTypeIntOptVar']
        autoPathRule= kwargs['shaderSpaceAutoPathRuleStrOptVar']
        nodeRules = kwargs['shaderSpaceNodeNameRuleStrOptVars']
        shaderRule = nodeRules[0]
        shadingRule = nodeRules[1]
        textureRule = nodeRules[2]
        bump2dRule = nodeRules[3]
        place2dRule = nodeRules[4]
        matinfoRule = nodeRules[5]
        options = kwargs['shaderSpaceOptionIntOptVars']
        assignToSelected = options[0]
        gammaCorrentMode = options[1]
        autoPathMode  = options[2]
        mirrorUvMode = options[3]
        sharedP2dMode = options[4]
        bumpValue = kwargs['shaderSpaceBumpValueFloatOptVar']
        replacements = kwargs['shaderSpaceNameStrOptVars']
        isAlphaIsLum = kwargs['shaderSpaceAlphaIsLuminanceIntOptVar']
        colorProfiles = kwargs['shaderSpaceColorProfileNameStrOptVars']
    except:
        raise
    # Check empty
    if not all(nodeRules):
        mc.warning('Maya nodes can not be empty')
        return '', ''
    elif not all(cnames):
        mc.warning('Channel abbreviations can not be empty')
        return '', ''
    elif not all(replacements):
        mc.warning('Name field can not be empty')
        return '', ''
    pSubstituteFunction = partial(
        _substituteVariables,
        asset=replacements[0],
        shader=replacements[1],
        user=replacements[2],
        version=replacements[3])
    if not _isExistsNodeType(shaderType):
        mc.warning(
            'Shader type is not exists. please check plug-in was appended')
        return '', ''
    # Shader name
    mainShader = pSubstituteFunction(shaderRule)
    # Save current selections
    previousSelected = mc.ls(
        sl=True, type=('mesh', 'nurbsSurface', 'transform'))
    # Shader name is invaild?
    if not isVaildName(mainShader):
        mc.warning('Invalid node name : '+mainShader)
        return '', ''
    # Is shader exists? if so, ask user.
    if mc.objExists(mainShader) and mc.confirmDialog(
        t='Exists', m='Shader is exists, continue?', button=['Yes', 'No'],
        db='Yes', cb='No', ds='No') == 'No': return '', ''
    # Shader create
    mainShader = mc.shadingNode(shaderType, name=mainShader, asShader=True)
    # Load preset, using source command
    if preset and preset != 'No Preset':
        presetPath = '{0}attrPresets/{1}/{2}.mel'.format(
            mc.internalVar(ups=True), shaderType, preset)
        if os.path.isfile(presetPath):
            mel.eval(r'applyPresetToNode "{0}" "" "" "{1}" 1'.format(
                mainShader, preset))
            print '{0} has been set : {1}'.format(mainShader, preset)
        else:
            mc.warning('Preset not found : {1}'.format(presetPath))
    # Shading Group create
    shadingGroup = mc.sets(renderable=True, noSurfaceShader=True,
        empty=True, name=pSubstituteFunction(shadingRule))
    # Rename material info
    materialInfo = mc.listConnections(shadingGroup,
        s=False, d=True, type='materialInfo')[0]
    materialInfo = mc.rename(materialInfo, pSubstituteFunction(matinfoRule))
    # Get connection pair
    connectTable = kRelatives[shaderType]
    # Connect shader to shading group, use different way
    if shaderType in kGeneralShadingGroupConnectMethod:
        _connectGeneralShadingGroup(mainShader, shadingGroup)
    elif shaderType in kMentalRayShadingGroupConnectMethod:
        _connectMentalRayShadingGroup(mainShader, shadingGroup)
    # Create and connect each channels
    newTextureList = []
    newTextureChannels = []
    for idx, pairs in enumerate(connectTable):
        if not checks[idx]:
            continue
        # Texture node create
        filenode = mc.shadingNode('file',
            name=pSubstituteFunction(textureRule, channel=cnames[idx]),
                asTexture=True)
        # aAttr is output attribute from texture,
        # bAttr is input attribute into shader.
        aAttr = pairs[0]
        bAttr = pairs[1]
        # This texture is a color map?
        withColorChannel = (aAttr == 'outColor')
        # Exclude bump map in VRay, because Bump map in VRay is outColor way.
        if shaderType in kVrayColorMangementShaders and bAttr == 'bumpMap':
            withColorChannel = False
        # Gamma correct setting :
        # In maya built-in shader or MentalRay, 
        # We need to set linear profile if is not color channel.
        # In VRay, we need to add VRay degamma attribute, 
        # And set it to sRGB if is color channel.
        if gammaCorrentMode:
            if shaderType in kColorManagementShaders and not withColorChannel:
                if kMayaVersion == '2014':
                    _setColorProfileOld(filenode, 2)
                elif kMayaVersion in ('2015', '2016'):
                    _setColorProfileNew(filenode, colorProfiles[1])
            elif shaderType in kColorManagementShaders and withColorChannel:
                if kMayaVersion == '2014':
                    # Do nothing
                    pass
                elif kMayaVersion in ('2015', '2016'):
                    _setColorProfileNew(filenode, colorProfiles[0])
            elif shaderType in kVrayColorMangementShaders and withColorChannel:
                _setVrayFileGamma(filenode,
                    kVrayDegammaMethod, kVrayDegammaValue)
        # If auto file path is 0(auto fill) or 1(auto fill is exists)
        if autoPathMode in (0, 1):
            fileTextureName = pSubstituteFunction(
                autoPathRule, channel=cnames[idx])
            if autoPathMode == 1 and not os.path.isfile(fileTextureName):
                # Skip not exists
                pass
            else:
                # Fill texture name
                mc.setAttr(filenode + '.fileTextureName',
                    fileTextureName, type='string')
        # If texture is outAlpha and AlphaIsLum mode is on
        if aAttr == 'outAlpha' and isAlphaIsLum:
            mc.setAttr(filenode+'.alphaIsLuminance', 1)
        # Set file's filter
        mc.setAttr(filenode+'.filterType', filterTypeIdx)
        # Here is deal with bump texture, index(9)
        if idx == 9:
            # Maya standard bump connect way
            if shaderType in kGeneralBumpMapMethod:
                _buildGeneralBumpMap(
                                    filenode+'.outAlpha',
                                    mainShader+'.normalCamera',
                                    pSubstituteFunction(bump2dRule), 
                                    bumpValue)
            # Mental ray bump connect way
            elif shaderType in kMentalRayBumpMapMethod:
                _buildGeneralBumpMap(
                                    filenode+'.outAlpha',
                                    mainShader+'.'+kMentalRayBumpMapChannel, 
                                    pSubstituteFunction(bump2dRule), 
                                    bumpValue)
            # Vray bump connect way
            elif shaderType in kVrayBumpMapMethod:
                _buildVrayBumpMap(
                                filenode+'.outColor',
                                mainShader+'.bumpMap',
                                bumpValue)
        else:
            mc.connectAttr(filenode+'.'+aAttr, mainShader+'.'+bAttr)
        newTextureList.append(filenode)
        newTextureChannels.append(cnames[idx])
    uvMirrorMethods = ((0, 0), (1,0), (0,1), (1,1))
    uvMirror = uvMirrorMethods[mirrorUvMode]
    # If Shared Place2dTexture is on,
    # we create a place2dTexture node connect to each map.
    place2dTextureNodeName = pSubstituteFunction(place2dRule)
    if sharedP2dMode == 0 and newTextureList:
        p2d = _buildPlace2dTexture(place2dTextureNodeName,
            uvMirror[0], uvMirror[1])
        for f in newTextureList:
            _connectToPlace2dTexture(f, p2d)
    # Otherwise, We need to create place2dTexture for each map.
    else:
        for idx, f in enumerate(newTextureList):
            # If user not provide <channel> flag,
            # It will suffix by alphabetic.
            if place2dRule.find('<channel>') == -1:
                p2d = _buildPlace2dTexture(
                    place2dTextureNodeName+'_'+chr(idx+65),
                        uvMirror[0], uvMirror[1])
            else:
                place2dTextureNodeName = pSubstituteFunction(
                    place2dRule, channel=newTextureChannels[idx])
                p2d = _buildPlace2dTexture(place2dTextureNodeName,
                    uvMirror[0], uvMirror[1])
            _connectToPlace2dTexture(f, p2d)
    # Assign to objects
    if assignToSelected == 1 and previousSelected:
        mc.select(previousSelected, r=True)
        mc.sets(e=True, fe=shadingGroup)
    mc.select(mainShader, r=True)
    return mainShader, shadingGroup

def _setColorProfileOld(filenode, colorProfile):
    # 0: Use Default Input Profile, 2: Linear sRGB, 3: sRGB
    mc.setAttr(filenode+'.colorProfile', colorProfile)

def _setColorProfileNew(filenode, colorProfile):
    if colorProfile in \
    mc.colorManagementCatalog(ltc=True, type='input'):
        mc.setAttr(filenode+'.colorSpace', colorProfile, typ='string')
    else:
        mc.warning(
            'The {0} is not in color transforms'.format(colorProfile))

def _setVrayFileGamma(filenode, colorspace, gamma):
    try:
        mel.eval('vray addAttributesFromGroup '+filenode+' vray_file_gamma 1;')
        mc.setAttr(filenode+'.vrayFileGammaEnable', True)
        mc.setAttr(filenode+'.vrayFileColorSpace', colorspace)
        mc.setAttr(filenode+'.vrayFileGammaValue', gamma)
    except:
        mc.warning('Failed to set {0} to vray file gamma'.format(filennode))
        raise

def _buildGeneralBumpMap(output_map, input_shader, bump2dName, bumpValue):
    bump2d = mc.shadingNode('bump2d', name=bump2dName, asUtility=True)
    mc.connectAttr(output_map, bump2d+'.bumpValue', f=True)
    mc.connectAttr(bump2d+'.outNormal', input_shader, f=True)
    mc.setAttr(bump2d+'.bumpDepth', bumpValue)
    # Set attribute alphaIsLuminance checked in bump map
    mc.setAttr(output_map.split('.')[0]+'.alphaIsLuminance', 1)

def _buildVrayBumpMap(output_map, input_shader, bumpValue):
    mc.connectAttr(output_map, input_shader, f=True)
    mc.setAttr(input_shader.split('.')[0]+'.bumpMult', bumpValue)

def _connectGeneralShadingGroup(shader, shadingGroup):
    mc.connectAttr(shader+'.outColor', shadingGroup+'.surfaceShader', f=True)

def _connectMentalRayShadingGroup(shader, shadingGroup):
    for attr in ('miMaterialShader', 'miShadowShader', 'miPhotonShader'):
        mc.connectAttr(shader+'.message', shadingGroup+'.'+attr, f=True)
