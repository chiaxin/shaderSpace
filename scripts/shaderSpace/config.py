import maya.cmds

kMayaVersion= maya.cmds.about( v = True )
kCurrentOS  = maya.cmds.about( os = True )
kLinearProfile = 'scene-linear Rec 709/sRGB'

# Vray color space - 0: linear, 1: Gamma, 2: sRGB
kVrayDegammaMethod = 1
kVrayDegammaValue = 2.2

kVersion = '0.4.12'
kLastUpdate = 'May, 18, 2016'

kWebsite = 'http://github.com/chiaxin/shaderSpace'

kDegammaValue = 0.454

# List shaders supported
kShadersList = ( \
'blinn', 'mia_material_x_passes', 'aiStandard', 'VRayMtl' )

kColorManagementShaders = ( \
'blinn', 'mia_material_x_passes'
)

kVrayColorMangementShaders = ( \
'VRayMtl' )

# The channel's name in tuple
'''
kChannelNames = ( \
'Color', 'Bump', 'Roughness', 'Glossiness', 'Reflectivity', \
'ReflectionColor', 'SpecularColor', 'Transparency', 'Incandescence' )
'''
kChannelNames = ( \
'Color', 'DiffuseWeight', 'Roughness', \
'Reflectance', 'ReflectionColor', 'ReflGlossiness', \
'Transparency', 'RefractionColor', 'RefraGlossiness', \
'Bump', 'Incandescence', 'Opacity' )

# This dictionary describe what plug-in necessary for shader
kShaderPlugins = { \
'blinn' : 'none', \
'mia_material_x_passes' : 'Mayatomr', \
'aiStandard' : 'mtoa', \
'VRayMtl' : 'vrayformaya' }

# This dictionary describe label text on the buttons
kShaderButtons = { \
'blinn' : 'Blinn ( Maya )', \
'mia_material_x_passes' : 'Material_x ( MentalRay )', \
'aiStandard' : 'AiStandard ( Arnold )', \
'VRayMtl' : 'VRayMtl ( VRay )' }

# This dictionary describe how to connect shading
kConnectSG = { \
### blinn
'blinn' : ( ('outColor', 'surfaceShader'), ), \
### mia_material_x_passes
'mia_material_x_passes' : ( \
('message', 'miMaterialShader' ), \
('message', 'miShadowShader' ), \
('message', 'miPhotonShader' ) ), \
### aiStandard
'aiStandard' : ( ('outColor', 'surfaceShader'), ), \
### VRayMtl
'VRayMtl' : ( ('outColor', 'surfaceShader'), ) \
}

kBumpChannel = { \
'blinn' : 'bump2d', \
'mia_material_x_passes' : 'bump2d', \
'aiStandard' : 'bump2d', \
'VRayMtl' : 'file'
}

# This dictionary describe how to connect channels
kRelatives = { \
### blinn
'blinn' : ( \
('outColor', 'color'),\
('outAlpha', 'diffuse'),\
('outAlpha', 'translucence'),\
('outAlpha', 'specularRollOff'),\
('outColor', 'specularColor'),\
('outAlpha', 'eccentricity'),\
('outColor', 'transparency'),\
('outColor', 'reflectedColor'),\
('outAlpha', 'reflectivity'),\
('outAlpha', 'normalCamera'),\
('outColor', 'incandescence'),\
('outAlpha', 'matteOpacity') ),\
### mia_material_x_passes
'mia_material_x_passes' : ( \
('outColor', 'diffuse'),\
('outAlpha', 'diffuse_weight'),\
('outAlpha', 'diffuse_roughness'),\
('outAlpha', 'reflectivity'),\
('outColor', 'refl_color'),\
('outAlpha', 'refl_gloss'),\
('outAlpha', 'transparency'),\
('outColor', 'refr_color'),\
('outAlpha', 'refr_gloss'),\
('outAlpha', 'standard_bump'),\
('outColor', 'additional_color'),\
('outAlpha', 'cutout_opacity') ),\
### aiStandard
'aiStandard' : ( \
('outColor', 'color'),\
('outAlpha', 'Kd'),\
('outAlpha', 'diffuseRoughness'),\
('outAlpha', 'Ks'),\
('outColor', 'KsColor'),\
('outAlpha', 'specularRoughness'),\
('outAlpha', 'Kt'),\
('outColor', 'KrColor'),\
('outAlpha', 'refractionRoughness'),\
('outAlpha', 'normalCamera'),\
('outColor', 'emissionColor'),\
('outColor', 'opacity') ),\
### VRayMtl
'VRayMtl' : ( \
('outColor', 'color'),\
('outAlpha', 'diffuseColorAmount'),\
('outAlpha', 'roughnessAmount'),\
('outAlpha', 'reflectionColorAmount'),\
('outColor', 'reflectionColor'),\
('outAlpha', 'reflectionGlossiness'),\
('outAlpha', 'refractionColorAmount'),\
('outColor', 'refractionColor'),\
('outAlpha', 'refractionGlossiness'),\
('outColor', 'bumpMap'),\
('outColor', 'illumColor'),\
('outColor', 'opacityMap') )
}

# Default options
optionsDefaultMaps = { \
'AST' : 'asset', \
'SDN' : 'shader', \
'USR' : 'user', \
'VER' : 'v01', \
'OPT' : [ 1, 1, 1, 0 ], \
'APR' : '<root>/sourceimages/<asset>/<asset><shader>_<channel>_<version>.tga', \
'CST' : [ 'col', 'dif', 'rhs', 'rfl', 'rlc', 'rlg', 'trs', 'rfc', 'rfg', 'bmp', 'inc', 'opc' ], \
'CCK' : [ 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0 ], \
'CFR' : [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], \
'BMP' : 0.1, \
'SNR' : '<asset>_<shader>_SD', \
'SGN' : '<asset>_<shader>_SG', \
'TEX' : '<asset>_<shader>_<channel>', \
'B2D' : '<asset>_<shader>_bump2d', \
'P2D' : '<asset>_<shader>_place2dTexture', \
'MIF' : '<asset>_<shader>_materialInfo', \
'IGN' : 0, \
'AIL' : 1 }

# OptionVars name
optionsVariableMaps = { \
'AST' : 'shaderSpaceAssetNameStrOptVar', \
'SDN' : 'shaderSpaceShaderNameStrOptVar', \
'USR' : 'shaderSpaceUserNameStrOptVar', \
'VER' : 'shaderSpaceVersionStrOptVar', \
'OPT' : 'shaderSpaceOptionsIntOptVars', \
'APR' : 'shaderSpaceAutoPathRuleStrOptVar', \
'CST' : 'shaderSpaceChannelShortStrOptVars', \
'CCK' : 'shaderSpaceChannelChecksIntOptVars', \
'CFR' : 'shaderSpaceChannelFiltersIntOptVars', \
'BMP' : 'shaderSpaceBumpIndexIntOptVar', \
'SNR' : 'shaderSpaceShaderNameRuleStrOptVar', \
'SGN' : 'shaderSpaceShadingGroupRuleStrOptVar', \
'TEX' : 'shaderSpaceTextureNodeRuleStrOptVar', \
'B2D' : 'shaderSpaceTextureBump2dRuleStrOptVar', \
'P2D' : 'shaderSpacePlace2dTextureRuleStrOptVar', \
'MIF' : 'shaderSpaceMaterialInfoRuleStrOptVar', \
'IGN' : 'shaderSpaceIgnoreTexWhenNotExistsIntOptVar', \
'AIL' : 'shaderSpaceAlphaIsLuminaIntOptVar' }

kChannelsPanelAnn = '''RMB can be change short name
Ctrl + RMB can be change texture filter
Alt + RMB can be change bump value
'''

kAssignAnn = 'Would be assign shader when created'
kGammaCorrectAnn = 'Would be make gamma correct in texture'
kAutoFileAnn = 'Would be set texture path automatically ( RMB can be set the rule )'
kMirrorAnn = 'Would be set place2dTexture mirror U, V or both ( RMB can be switch )'

kAboutContent = '''About Shader Space

Author : Chia Xin Lin

Contact : nnnight@gmail.com

Version : ''' + kVersion + '\n\n' + '''\
Last Update : ''' + kLastUpdate + '\n\n' +'''\
The Shader Space tool be able to create a shader with texture connections,
And provide some useful option and functions. If you have any questions,
even suggestions or requires, You can send e-mail to tell me, Thanks.
'''
