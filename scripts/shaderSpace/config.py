import maya.cmds
kMayaVersion = maya.cmds.about( v = True )
kCurrentOS = maya.cmds.about( os = True )

kDegammaValue = 0.454

kChannelNames = ( \
'Color', 'Bump', 'Roughness', 'Glossiness', 'Reflectivity', \
'Reflection Color', 'Specular Color', 'Transparency', 'Incandescence' )

kShaderPlugins = { \
'blinn' : 'none',
'mia_material_x_passes' : 'Mayatomr',
'aiStandard' : 'mtoa',
'VRayMtl' : 'vrayformaya' }

kShaderButtons = { \
'blinn' : 'blinn',
'mia_material_x_passes' : 'material_x',
'aiStandard' : 'aiStandard',
'VRayMtl' : 'VRayMtl' }

kConnectSG = { \
'blinn' : [ ('outColor', 'surfaceShader') ],
'mia_material_x_passes' : [ \
('message', 'miMaterialShader' ), \
('message', 'miShadowShader' ), \
('message', 'miPhotonShader' ) ], \
'aiStandard' : [ ('outColor', 'surfaceShader') ], \
'VRayMtl' : [ ('outColor', 'surfaceShader') ] }

kRelatives = { \
'blinn' : [ \
('outColor', 'color'),\
('outAlpha', 'normalCamera'),\
('outColor', 'reflectedColor'),\
('outAlpha', 'specularRollOff'),\
('outAlpha', 'eccentricity'),\
('outColor', 'transparency'),\
('outColor', 'specularColor'),\
('outAlpha', 'reflectivity'),\
('outColor', 'incandescence') ], \
'mia_material_x_passes' : [ \
('outColor', 'diffuse'),\
('outAlpha', 'standard_bump'),\
('outAlpha', 'reflectivity'),\
('outAlpha', 'refl_gloss'),\
('outAlpha', 'diffuse_roughness'),\
('outAlpha', 'transparency'),\
('outColor', 'refl_color'),\
('outColor', 'refl_falloff_color'),\
('outColor', 'additional_color') ], \
'aiStandard' : [ \
('outColor', 'color'),\
('outAlpha', 'normalCamera'),\
('outAlpha', 'Kr'),\
('outAlpha', 'Ks'),\
('outAlpha', 'specularRoughness'),\
('outAlpha', 'Kt'),\
('outColor', 'KrColor'),\
('outColor', 'KsColor'),\
('outColor', 'emissionColor') ], \
'VRayMtl' : [ \
('outColor', 'color'),\
('outColor', 'bumpMap'),\
('outAlpha', 'reflectionColorAmount'),\
('outAlpha', 'reflectionGlossiness'),\
('outAlpha', 'roughnessAmount'),\
('outAlpha', 'refractionColorAmount'),\
('outColor', 'reflectionColor'),\
('outColor', 'reflectionExitColor'),\
('outColor', 'illumColor') ] }

optionsDefaultMaps = { \
'AST' : 'asset', \
'SDN' : 'shader', \
'USR' : 'user', \
'VER' : 'v01', \
'OPT' : [ 1, 1, 1, 0 ], \
'APR' : '<root>/sourceimages/<asset>/<asset><shader>_<channel>_<version>.tga', \
'CST' : ['col', 'bmp', 'rhs', 'gls', 'rfl', 'rlc', 'spc', 'trs', 'inc'], \
'CCK' : [ 1, 1, 1, 0, 0, 0, 0, 0, 0 ], \
'CFR' : [ 0, 0, 0, 0 ,0 ,0 ,0 ,0 ,0 ], \
'BMP' : 0.1, \
'SNR' : '<asset>_<shader>_SD', \
'SGN' : '<asset>_<shader>_SG', \
'TEX' : '<asset>_<shader>_<channel>', \
'B2D' : '<asset>_bump2d', \
'P2D' : '<asset>_place2dTexture', \
'MIF' : '<asset>_materialInfo', \
'IGN' : 0, \
'AIL' : 1 }

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

kAboutContent = \
'Author : Chia Xin Lin\n\n' \
'Contact : nnnight@gmail.com\n\n' \
'Version : 0.2.3\n\n' \
'Last Update : 01/19/2016\n\n' \
'The Shader Space tool be able to create a shader with texture connections,' \
'And provide some useful option and functios.If you have any questions,' \
'even suggestions, You can send e-mail to tell me, Thanks.' \

