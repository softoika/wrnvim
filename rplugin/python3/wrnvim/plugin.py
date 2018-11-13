import neovim
import os
import yaml
import re
from datetime import date, datetime, timedelta
from . import config
from .smtp_send import create_message
from .smtp_send import send


@neovim.plugin
class WrNvimPlugin(object):

    def __init__(self, vim):
        self.vim = vim
        if self.__exists_vim_variable('g:clear_text_on_wrnew'):
            config.clear_text_on_wrnew = vim.eval('g:clear_text_on_wrnew')

    def __load_send_yaml(self):
        '''
        g:sendyaml_pathに設定されたパスにあるsend.ymlから設定を読み込む
        '''
        path = self.vim.eval('g:sendyml_path')
        with open(os.path.join(path, config.send_yaml)) as f:
            return yaml.load(f)

    def __current_buffer(self):
        buf = self.vim.current.buffer[:]
        return '\n'.join(buf)

    def __load_wr(self):
        '''
        カレントバッファからメールのタイトルと本文を正規表現で取得する
        '''
        text = self.__current_buffer()
        pt = r'(?<=title:\n).*'
        pb = r'(?<=body:\n).*'
        mt = re.search(pt, text, flags=re.MULTILINE)
        mb = re.search(pb, text, flags=(re.MULTILINE | re.DOTALL))
        if mt and mb:
            return (mt.group(0), mb.group(0))

    @neovim.command('WrSend')
    def send(self):
        if self.__exists_vim_variable('g:sendyml_path'):
            param = self.__load_send_yaml()
            title, body = self.__load_wr()
            if title and body:
                msg = create_message(param['from'], param['to'], title, body)
                send(param['server'], param['password'], msg)
                self.vim.command('echo "SUCCESS!"')
        else:
            self.vim.command('echo "Not found g:sendyml_path"')

    def __thisweek(self, weekday='fri'):
        weekdays = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4,
                    'sat': 5, 'sun': 6}
        today = date.today()
        if today.weekday() < weekdays[weekday]:
            return today + timedelta(days=weekdays[weekday] - today.weekday())
        else:
            return today - timedelta(days=today.weekday() - weekdays[weekday])

    @neovim.command('WrNew')
    def new(self):
        text = self.__current_buffer()
        ptd = r'(?<=WR_)\d+'
        pbd = r'\d{4}年\d\d月\d\d日'
        new_td = self.__thisweek().strftime('%Y%m%d')
        new_bd = self.__thisweek().strftime('%Y年%m月%d日')
        text = re.sub(ptd, new_td, text)
        text = re.sub(pbd, new_bd, text)
        self.vim.vars['text'] = text.split('\n')
        self.vim.command(f'call writefile(g:text, "{new_td}.wr")')
        self.vim.command(f'e {new_td}.wr')
        if config.clear_text_on_wrnew:
            self.clear()
        
    @neovim.command('WrClear')
    def clear(self):
        '''
        労働時間以外の各項目の内容を削除する
        '''
        text = self.__current_buffer()
        p = r"(?<=[-=]{5}\n).*?(?=■|[-=]{5}|$)"
        matches = re.finditer(p, text, flags=re.DOTALL)
        # 最初の項目(労働時間)を無視する
        matches.__next__()
        for m in matches:
            g = m.group(0) if m.group(0) else '\n'
            text = text.replace(g, '\n')
        self.__replace_buffer(text)

    def __replace_buffer(self, text):
        self.vim.vars['lines'] = self.__delete_redundant_line(text.split('\n'))
        self.vim.command('0,$delete')
        self.vim.command('call append(0, g:lines)')

    def __delete_redundant_line(self, lines):
        new_lines = [lines[0]]
        prev = lines[0]
        for line in lines[1:]:
            if prev != '' or line != '':
                new_lines.append(line)
            prev = line
        return new_lines

    def __highlight(self):
        self.vim.command('call matchadd("Comment", "--.*", 0)')
        self.vim.command('call matchadd("Comment", "==.*", 0)')
        self.vim.command('call matchadd("Constant", "[0-9]", 1)')
        self.vim.command('call matchadd("Function", "■.*", 0)')
        self.vim.command('call matchadd("Statement", "^[a-zA-Z]*:", 0)')

    @neovim.autocmd('BufNewFile', pattern='*.wr')
    def on_bufnewfile(self):
        self.__highlight()

    @neovim.autocmd('BufRead', pattern='*.wr')
    def on_bufread(self):
        self.__highlight()

    def __exists_vim_variable(self, name):
        return self.vim.eval(f'exists("{name}")')
