import neovim
import os
import yaml
import re
from datetime import date, timedelta
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

    def _current_buffer(self):
        buf = self.vim.current.buffer[:]
        return '\n'.join(buf)

    def _load_wr(self):
        '''
        カレントバッファからメールのタイトルと本文を正規表現で取得する
        '''
        text = self._current_buffer()
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
                msg = create_message(settings['from'],
                                     settings['to'], title, body)
                send(settings['server'], settings['password'], msg)
                self.vim.command('echo "SUCCESS!"')
        else:
            self.vim.command('echo "Not found g:sendyml_path"')

    def _thisweek(self, weekday='fri'):
        weekdays = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4,
                    'sat': 5, 'sun': 6}
        today = date.today()
        if today.weekday() < weekdays[weekday]:
            return today + timedelta(days=weekdays[weekday] - today.weekday())
        else:
            return today - timedelta(days=today.weekday() - weekdays[weekday])

    @neovim.command('WrNew')
    def new(self):
        text = self._current_buffer()
        ptd = r'(?<=WR_)\d+'
        pbd = r'\d{4}年\d\d月\d\d日'
        new_td = self._thisweek().strftime('%Y%m%d')
        new_bd = self._thisweek().strftime('%Y年%m月%d日')
        text = re.sub(ptd, new_td, text)
        text = re.sub(pbd, new_bd, text)
        self.vim.vars['text'] = text.split('\n')
        self.vim.command(f'call writefile(g:text, "{new_td}.wr")')
        self.vim.command(f'e {new_td}.wr')

    def _highlight(self):
        self.vim.command('call matchadd("Comment", "--.*", 0)')
        self.vim.command('call matchadd("Comment", "==.*", 0)')
        self.vim.command('call matchadd("Constant", "[0-9]", 1)')
        self.vim.command('call matchadd("Function", "■.*", 0)')
        self.vim.command('call matchadd("Statement", "^[a-zA-Z]*:", 0)')

    @neovim.autocmd('BufNewFile', pattern='*.wr')
    def on_bufnewfile(self):
        self._highlight()

    @neovim.autocmd('BufRead', pattern='*.wr')
    def on_bufread(self):
        self._highlight()
