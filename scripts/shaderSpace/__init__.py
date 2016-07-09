'''
==========================================================
Initial for shaderSpace Rapid Shader Workflow Tool in Maya

Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
E-Mail : nnnight@gmail.com
Github : http://github.com/chiaxin
==========================================================
'''
from UI import ShaderSpaceMainWin

try:
    shaderSpaceMainUI.close()
    shaderSpaceMainUI.show()
except:
    shaderSpaceMainUI = ShaderSpaceMainWin()
    shaderSpaceMainUI.show()
finally:
    pass
