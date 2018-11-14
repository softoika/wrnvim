# wrnvim
## Dependency
- Neovim
- Python3

## Installation (Dein.vim)
dein.toml example
```toml
[[plugins]]
repo = 'softoika/wrnvim'
hook_add = '''
let g:sendyml_path="/path/to/dir"
'''
```

# [Debug on Python REPL](https://github.com/neovim/python-client#usage-through-the-python-repl)
## Dependency
- pipenv
## Connect Python REPL with Nvim
Start Nvim with a known address:
```
$ NVIM_LISTEN_ADDRESS=/tmp/nvim nvim
```
In another terminal, connect a python REPL by using nvimrepl.sh
```
$ ./nvimrepl.sh
```
