import neovim
import os
import yaml
import re
import send

@neovim.plugin
class WrNvim(object):
    SEND_YAML = 'send.yml'

    def __init__(self, vim):
        self.vim = vim

    def load_settings(self):
        '''
        g:sendyaml_pathに設定されたパスにあるsend.ymlから設定を読み込む
        '''
        path = self.vim.eval('g:sendyml_path')
        with open(os.path.join(path, SEND_YAML)) as f:
            settings = yaml.load(f)

    def load_wr(self):
        '''
        カレントバッファからメールのタイトルと本文を正規表現で取得する
        '''
        buf = self.nvim.current.buffer[:]
        text = '\n'.join(buf)
        pt = r'(?<title:\n).*'
        pb = r'(?<=body:\n).*'
        mt = re.search(pt, t, flags=re.MULTILINE)
        mb = re.search(pb, t, flags=(re.MULTILINE | re.DOTALL))
        if mt and mb:
            return (mt.group(0), mb.group(0))

    @neovim.command('WrSend')
    def send(self):
        if self.vim.eval('exists("g:sendyml_path")'):
            settings = self.load_settings()
            title, body = self.load_wr()
            msg = send.create_message(settings['server'], settings['password'], title, body)
            send.send(settings['server'], settings['password'], msg)
            self.nvim.command('echo "SUCCESS!"')
        else:
        else:
            self.nvim.command('echo "Not found g:sendyml_path"')
        
    @neovim.command('HelloNvim')
    def hello:
        self.nvim.command('echo "Hello Neovim"')
