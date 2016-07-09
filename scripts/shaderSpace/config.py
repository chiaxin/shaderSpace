'''
    Configurations for shaderSpace Rapid Shader Workflow Tool in Maya

    Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
    E-Mail : nnnight@gmail.com
    Github : http://github.com/chiaxin
'''
import maya.cmds

kMayaVersion= maya.cmds.about(v=True)
kCurrentOS  = maya.cmds.about(os=True)
kLinearProfile = 'scene-linear Rec 709/sRGB'

# Vray color space - 0: linear, 1: Gamma, 2: sRGB
kVrayDegammaMethod = 1
kVrayDegammaValue = 2.2
kVersion = '0.5.04'
kLastUpdate = 'Jul, 09, 2016'
kWebsite = 'http://github.com/chiaxin/shaderSpace'

# List shaders supported
kShadersList = ('blinn', 'mia_material_x_passes', 'aiStandard', 'VRayMtl')
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
    'shaderSpaceNameStrOptVars':['asset', 'shader', 'user', 'v01'],
    'shaderSpaceChannelsIntOptVars':[2, 0, 0, 2, 0, 2, 0, 0, 0, 2, 0, 0],
    'shaderSpaceShaderIntOptVar':0,
    'shaderSpaceOptionIntOptVars':[1, 0, 1, 0, 0],
    'shaderSpaceBumpValueFloatOptVar':0.1,
    'shaderSpaceAlphaIsLuminanceIntOptVar':2,
    'shaderSpaceFilterTypeIntOptVar':1,
    'shaderSpaceAbbreviationsStrOptVars':['col', 'dif', 'rough',
    'rfl', 'spc', 'gls', 'trs', 'rfc', 'rfg', 'bmp', 'inc', 'opc'],
    'shaderSpaceAutoPathRuleStrOptVar'\
    :'<root>/sourceimages/<asset>/<asset>_<shader>_<channel>_<version>.tga',
    'shaderSpaceNodeNameRuleStrOptVars'\
    :['<asset>_<shader>_SD', '<asset>_<shader>_SG',\
    '<asset>_<shader>_<channel>', '<asset>_<shader>_bmp2d', \
    '<asset>_<shader>_place2dTexture', '<asset>_<shader>_materialInfo'],
    'shaderSpaceToolsPathStrOptVars':['', '', '', '', ''],
    'shaderSpaceUvSnapshotOptionIntOptVars':[0, 1, 1, 0],
    'shaderSpacePhotoshopNamesStrOptVars':['', ''],
    'shaderSpacePhotoshopOptionIntOptVars':[1],
    'shaderSpaceShaderExportIntOptVars':[0],
    'shaderSpacePolygonExportOptionIntOptVars':[0, 0],
    'shaderSpacePolygonExportOptionStrOptVars':['', '']
    }
