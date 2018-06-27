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
hook_post_update = '''
call dein#remote_plugins()
'''
```
