# -*- coding: utf-8 -*-
# Initial for shaderSpace Module
#
# Made by Chia Xin Lin, Copyright (c) 2016 by Chia Xin Lin
#
# E-Mail : nnnight@gmail.com
#
# Github : http://github.com/chiaxin
#
# Licensed under MIT: https://opensource.org/licenses/MIT
#
import UI
#
try:
    _SHADERSPACEWIN.show()
except:
    _SHADERSPACEWIN = UI.ShaderSpaceMainWin()
    _SHADERSPACEWIN.show()
    print '# shaderSpace UI has been created.'
else:
    print '# shaderSpace UI is exists, just show it'

# Python init script end #
