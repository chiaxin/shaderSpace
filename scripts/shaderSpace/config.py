# -*- coding: utf-8 -*-
# shaderSpace configuration
#
# Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
#
# E-Mail : nnnight@gmail.com
#
# Github : http://github.com/chiaxin
#
# Licensed under MIT: https://opensource.org/licenses/MIT
#
import maya.cmds

kMayaVersion= maya.cmds.about(v=True)
kCurrentOS  = maya.cmds.about(os=True)
kSRgbProfile = u'sRGB'
kLinearProfile = u'scene-linear Rec 709/sRGB'

# Vray color space - 0: linear, 1: Gamma, 2: sRGB
kVrayDegammaMethod = 1
kVrayDegammaValue = 2.2
kVersion = '1.0.02 release'
kLastUpdate = 'Nov, 12, 2016'
kWebsite = 'http://github.com/chiaxin/shaderSpace'

# List shaders supported
kShadersList = ('blinn',
                'mia_material_x_passes',
                'aiStandard',
                'VRayMtl')
kColorManagementShaders = ('blinn', 'mia_material_x_passes')
kVrayColorMangementShaders = ('VRayMtl')
kGeneralBumpMapMethod = ('blinn', 'aiStandard')
kMentalRayBumpMapMethod = ('mia_material_x_passes')
kMentalRayBumpMapChannel = 'standard_bump'
kVrayBumpMapMethod = ('VRayMtl')
kGeneralShadingGroupConnectMethod = ('blinn', 'aiStandard', 'VRayMtl')
kMentalRayShadingGroupConnectMethod = ('mia_material_x_passes')

# The channel's name in tuple
kChannelList = ('Color',
                'DiffuseWeight',
                'Roughness',
                'Reflectance',
                'ReflectionColor',
                'ReflGlossiness',
                'Transparency',
                'RefractionColor', 
                'RefraGlossiness', 
                'Bump',
                'Incandescence',
                'Opacity'
)
# This dictionary describe how to connect channels
kRelatives = {  'blinn':(
                ('outColor', 'color'),
                ('outAlpha', 'diffuse'),
                ('outAlpha', 'translucence'),
                ('outAlpha', 'specularRollOff'),
                ('outColor', 'specularColor'),
                ('outAlpha', 'eccentricity'),
                ('outColor', 'transparency'),
                ('outColor', 'reflectedColor'),
                ('outAlpha', 'reflectivity'),
                ('outAlpha', 'normalCamera'),
                ('outColor', 'incandescence'),
                ('outAlpha', 'matteOpacity')
                ),
                'mia_material_x_passes':(
                ('outColor', 'diffuse'),
                ('outAlpha', 'diffuse_weight'),
                ('outAlpha', 'diffuse_roughness'),
                ('outAlpha', 'reflectivity'),
                ('outColor', 'refl_color'),
                ('outAlpha', 'refl_gloss'),
                ('outAlpha', 'transparency'),
                ('outColor', 'refr_color'),
                ('outAlpha', 'refr_gloss'),
                ('outAlpha', 'standard_bump'),
                ('outColor', 'additional_color'),
                ('outAlpha', 'cutout_opacity')
                ),
                'aiStandard':(
                ('outColor', 'color'),
                ('outAlpha', 'Kd'),
                ('outAlpha', 'diffuseRoughness'),
                ('outAlpha', 'Ks'),
                ('outColor', 'KsColor'),
                ('outAlpha', 'specularRoughness'),
                ('outAlpha', 'Kt'),
                ('outColor', 'KrColor'),
                ('outAlpha', 'refractionRoughness'),
                ('outAlpha', 'normalCamera'),
                ('outColor', 'emissionColor'),
                ('outColor', 'opacity')
                ),
                'VRayMtl':(
                ('outColor', 'color'),
                ('outAlpha', 'diffuseColorAmount'),
                ('outAlpha', 'roughnessAmount'),
                ('outAlpha', 'reflectionColorAmount'),
                ('outColor', 'reflectionColor'),
                ('outAlpha', 'reflectionGlossiness'),
                ('outAlpha', 'refractionColorAmount'),
                ('outColor', 'refractionColor'),
                ('outAlpha', 'refractionGlossiness'),
                ('outColor', 'bumpMap'),
                ('outColor', 'illumColor'),
                ('outColor', 'opacityMap'))
}
kDefaultMappings={
    'shaderSpaceNameStrOptVars':[u'asset', u'shader', u'user', u'v01'],
    'shaderSpaceChannelsIntOptVars':[2, 0, 0, 2, 0, 2, 0, 0, 0, 2, 0, 0],
    'shaderSpaceShaderIntOptVar':0,
    'shaderSpaceOptionIntOptVars':[1, 0, 1, 0, 0],
    'shaderSpaceBumpValueFloatOptVar':0.1,
    'shaderSpaceAlphaIsLuminanceIntOptVar':2,
    'shaderSpaceFilterTypeIntOptVar':1,
    'shaderSpaceAbbreviationsStrOptVars':[
                                        u'col',
                                        u'dif',
                                        u'rough',
                                        u'rfl',
                                        u'spc',
                                        u'gls',
                                        u'trs',
                                        u'refraCo',
                                        u'refraGls',
                                        u'bmp',
                                        u'inc',
                                        u'opc'],
    'shaderSpaceAutoPathRuleStrOptVar'\
    :u'<root>/sourceimages/<asset>/<asset>_<shader>_<channel>_<version>.tga',
    'shaderSpaceNodeNameRuleStrOptVars'\
    :[u'<asset>_<shader>_SD', u'<asset>_<shader>_SG',\
    u'<asset>_<shader>_<channel>', u'<asset>_<shader>_bmp2d', \
    u'<asset>_<shader>_place2dTexture', u'<asset>_<shader>_materialInfo'],
    'shaderSpaceToolsPathStrOptVars':[u'', u'', u'', u'', u''],
    'shaderSpaceUvSnapshotOptionIntOptVars':[0, 1, 1, 0],
    'shaderSpacePhotoshopOptionIntOptVars':[1, 0],
    'shaderSpaceShaderExportIntOptVars':[0, 0],
    'shaderSpacePolygonExportOptionIntOptVars':[0, 0],
    'shaderSpacePolygonExportOptionStrOptVars':[u'', u''],
    'shaderSpaceSettingsLockedIntOptVar': 0,
    'shaderSpaceColorProfileNameStrOptVars': [kSRgbProfile, kLinearProfile]
    }

kAboutInfo = ('Shader Space : Create Shader Toolset in Maya',
              '--------------------------------------------',
              'Support Maya version : 2014, 2015, 2016'
              'Support Shader : ' + ', '.join(kShadersList),
              'Author : Chia Xin Lin',
              'Current Version : ' + kVersion,
              'Last Update : ' + kLastUpdate,
              'Contact me --- ',
              'E-Mail : nnnight@gmail.com',
              'Github : http://github.com/chiaxin',
              'Blogger : http://cgdeparture.blogspot.tw',
              'If you have any question or suggestions, please feel free to contact me. Thanks')
