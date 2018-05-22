import neovim

@neovim.plugin
class WrHighlight:
    def __init__(self, vim):
        self.vim = vim
    
