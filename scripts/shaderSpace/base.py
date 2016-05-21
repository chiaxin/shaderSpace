import maya.cmds as mc

class BaseUI:
    Win = 'BASE_UI'
    Frl = 'BASE_UI_FRL'
    width = 240
    height= 360

    def build(self, menu, blocks , uit, title):
        self.destroy()
        mc.window(self.Win, w=self.width, h=self.height, t=title)
        if uit is not None:
            uit.build()
            uit.push()

        if menu is not None: menu.build()

        self.Frl = mc.frameLayout(self.Frl)

        if blocks is not None and len(blocks):
            for block in blocks:
                block.build()

        mc.setParent('..')

        if uit is not None: uit.pop()

    def destroy(self):
        if self.exists():
            mc.deleteUI(self.Win)

    def exists(self):
        return mc.window(self.Win, q=True, ex=True)

    def show(self):
        if self.exists():
            mc.showWindow(self.Win)
            mc.window(self.Win, e=True, w=self.width, h=self.height)

class BaseUIT:
    Uit = 'BASE_UIT'

    def build(self):
        if mc.uiTemplate(self.Uit, q=True, ex=True):
            mc.deleteUI(self.Uit, uit=True)
        mc.uiTemplate(self.Uit)
        self.templates()

    def templates(self):
        # Control
        mc.button(dt=self.Uit, h=30)
        mc.text(dt=self.Uit, font='fixedWidthFont', w=100)
        mc.textField(dt=self.Uit, w=150, h=26)
        mc.textFieldGrp(dt=self.Uit, w=300, h=30, cw2=(80, 240))
        mc.textFieldButtonGrp(dt=self.Uit, w=320, cw3=(80, 240, 60), bl='browse')

        # Layout
        mc.frameLayout(dt=self.Uit, cl=False, cll=False, lv=False, mh=5, mw=5)
        mc.columnLayout(dt=self.Uit, adj=True , rs=3, cal='left')
        mc.radioButtonGrp(dt=self.Uit, cw4=(60, 60, 60, 60), cw3=(60, 60, 60))

    def push(self):
        mc.setUITemplate(self.Uit, pushTemplate=True)

    def pop(self):
        mc.setUITemplate(popTemplate=True)

class BaseBlock:
    Frl = 'BLOCK_FRL'
    Label = 'Base Block'
    width = 256
    height= 128

    def build(self):
        self.Frl = mc.frameLayout(self.Frl, l=self.Label, w=self.width, h=self.height)
        self.content()
        mc.setParent('..')

    def content(self): # This must to override
        pass
