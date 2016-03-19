import maya.cmds

kMayaVersion= maya.cmds.about( v = True )
kCurrentOS  = maya.cmds.about( os = True )
kLinearProfile = 'scene-linear Rec 709/sRGB'

kVersion = '0.3.4'
kLastUpdate = 'Mar, 19, 2016'

kWebsite = 'http://github.com/chiaxin/shaderSpace'

kDegammaValue = 0.454

# List shaders supported
kShadersList = ( \
'blinn', 'mia_material_x_passes', 'aiStandard', 'VRayMtl' )

kColorManagementShaders = ( \
'blinn', 'mia_material_x_passes'
)

# The channel's name in tuple
kChannelNames = ( \
'Color', 'Bump', 'Roughness', 'Glossiness', 'Reflectivity', \
'ReflectionColor', 'SpecularColor', 'Transparency', 'Incandescence' )

# This dictionary describe what plug-in necessary for shader
kShaderPlugins = { \
'blinn' : 'none', \
'mia_material_x_passes' : 'Mayatomr', \
'aiStandard' : 'mtoa', \
'VRayMtl' : 'vrayformaya' }

# This dictionary describe label text on the buttons
kShaderButtons = { \
'blinn' : 'Blinn ( Maya )', \
'mia_material_x_passes' : 'Material_x ( Mental Ray )', \
'aiStandard' : 'AiStandard ( Arnold )', \
'VRayMtl' : 'VRayMtl ( V Ray )' }

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
('outAlpha', 'normalCamera'),\
('outAlpha', 'reflectivity'),\
('outAlpha', 'eccentricity'),\
('outAlpha', 'specularRollOff'),\
('outColor', 'reflectedColor'),\
('outColor', 'specularColor'),\
('outColor', 'transparency'),\
('outColor', 'incandescence') ),
### mia_material_x_passes
'mia_material_x_passes' : ( \
('outColor', 'diffuse'),\
('outAlpha', 'standard_bump'),\
('outAlpha', 'diffuse_roughness'),\
('outAlpha', 'refl_gloss'),\
('outAlpha', 'reflectivity'),\
('outColor', 'refl_color'),\
('outColor', 'refl_falloff_color'),\
('outAlpha', 'transparency'),\
('outColor', 'additional_color') ),
### aiStandard
'aiStandard' : ( \
('outColor', 'color'),\
('outAlpha', 'normalCamera'),\
('outAlpha', 'diffuseRoughness'),\
('outAlpha', 'specularRoughness'),\
('outAlpha', 'Ks'),\
('outAlpha', 'KsColor'),\
('outColor', 'KrColor'),\
('outColor', 'Kt'),\
('outColor', 'emissionColor') ),\
### VRayMtl
'VRayMtl' : ( \
('outColor', 'color'),\
('outColor', 'bumpMap'),\
('outAlpha', 'roughnessAmount'),\
('outAlpha', 'reflectionGlossiness'),\
('outAlpha', 'reflectionColorAmount'),\
('outAlpha', 'reflectionColor'),\
('outColor', 'reflectionExitColor'),\
('outAlpha', 'refractionColorAmount'),\
('outColor', 'illumColor') )\
}

# Default options
optionsDefaultMaps = { \
'AST' : 'asset', \
'SDN' : 'shader', \
'USR' : 'user', \
'VER' : 'v01', \
'OPT' : ( 1, 1, 1, 0 ), \
'APR' : '<root>/sourceimages/<asset>/<asset><shader>_<channel>_<version>.tga', \
'CST' : ( 'col', 'bmp', 'rhs', 'gls', 'rfl', 'rlc', 'spc', 'trs', 'inc' ), \
'CCK' : ( 1, 1, 1, 0, 0, 0, 0, 0, 0 ), \
'CFR' : ( 0, 0, 0, 0 ,0 ,0 ,0 ,0 ,0 ), \
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

kAssignAnn = 'Assign ON would be assign shader when created'
kGammaCorrectAnn = 'Gamma Correct ON would be make gamma correct'
kAutoFileAnn = 'Auto File ON would be set texture path automatically ( RMB can be set the rule )'
kMirrorAnn = 'Mirror ON would be set place2dTexture mirror U, V or both ( RMB can be switch )'

kAboutContent = '''About Shader Space

Author : Chia Xin Lin

Contact : nnnight@gmail.com

Version : ''' + kVersion + '\n\n' + '''\
Last Update : ''' + kLastUpdate + '\n\n' +'''\
The Shader Space tool be able to create a shader with texture connections,
And provide some useful option and functions. If you have any questions,
even suggestions or requires, You can send e-mail to tell me, Thanks.
'''
