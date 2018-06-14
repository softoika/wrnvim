import neovim
import os
import yaml
import re
from .smtp_send import create_message
from .smtp_send import send

@neovim.plugin
class WrNvim(object):
    SEND_YAML = 'send.yml'

    def __init__(self, vim):
        self.vim = vim

    def _load_settings(self):
        '''
        g:sendyaml_pathに設定されたパスにあるsend.ymlから設定を読み込む
        '''
        path = self.vim.eval('g:sendyml_path')
        with open(os.path.join(path, WrNvim.SEND_YAML)) as f:
            settings = yaml.load(f)
            return settings

    def _load_wr(self):
        '''
        カレントバッファからメールのタイトルと本文を正規表現で取得する
        '''
        buf = self.vim.current.buffer[:]
        text = '\n'.join(buf)
        pt = r'(?<=title:\n).*'
        pb = r'(?<=body:\n).*'
        mt = re.search(pt, text, flags=re.MULTILINE)
        mb = re.search(pb, text, flags=(re.MULTILINE | re.DOTALL))
        if mt and mb:
            return (mt.group(0), mb.group(0))
    
    @neovim.command('WrSend')
    def send(self):
        if self.vim.eval('exists("g:sendyml_path")'):
            settings = self._load_settings()
            title, body = self._load_wr()
            if title and body:
                msg = create_message(settings['from'], settings['to'], title, body)
                send(settings['server'], settings['password'], msg)
                self.vim.command('echo "SUCCESS!"')
        else:
            self.vim.command('echo "Not found g:sendyml_path"')
        
    def _highlight(self):
        self.vim.command('call matchadd("Comment", "--.*", 0)')
        self.vim.command('call matchadd("Comment", "==.*", 0)')
        self.vim.command('call matchadd("Constant", "\d", 0)')
        self.vim.command('call matchadd("Function", "■.*", 0)')
        self.vim.command('call matchadd("Statement", "^[0-9a-zA-Z\-_]+:", 0)')

    @neovim.autocmd('BufNewFile', pattern='*.wr')
    def on_bufnewfile(self):
        self._highlight()

    @neovim.autocmd('BufRead', pattern='*.wr')
    def on_bufread(self):
        self._highlight()

