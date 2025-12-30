# Vim Setup

## Some initial options:
in ~/.vimrc:
```
syntax on "syntax color highlighting
filetype plugin indent on   "enable filetype events, 
							"filetype-based plugin loading, and
							"filetype-based indentation
set tabstop=4 softtabstop=4 shiftwidth=4 expandtab autoindent smartindent
	" Set tabes to a width of 4
	" expandtab: swap out a tab for spaces
	" autoindent: inherit indentation from current line when making newline
	" smartindent: extends autoindent to add some C-family indentation rules
set number relativenumber " show line numbers (current line: absolute, other lines: relative)
```

## Install Vim Plug
in terminal:
```
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```

## Plug Coc
in ~/.vimrc:
```
call plug#begin()

Plug 'neoclide/coc.nvim', {'branch': 'release'}

call plug#end()
```
### Reopen vimrc and install
```
:PlugInstall
```
### Configure Coc

Some of [these](https://github.com/neoclide/coc.nvim/wiki/Completion-with-sources#use-tab-or-custom-key-for-trigger-completion) options may be useful.

### Install nodejs & npm
in terminal:
```
sudo dnf install nodejs
```

### Install yarn
in terminal:
```
sudo npm install yarn
```

### Build Coc with yarn
in terminal:
```
cd .vim/plugged/coc.nvim/
yarn install
```

## Install Language server bindings
in terminal:
```
cd ~
vim .vimrc
:CocInstall coc-clangd coc-als @yaegassy/coc-pylsp
```
## Install clangd
opening a c++ file will usually trigger language server install
```
vim hello.cpp
:CocCommand clangd.install
```

## Colors are busted
in ~/.vimrc:
```
" ...
Plug 'junegunn/seoul256.vim'
" ...

colorscheme seoul256 " Color scheme
hi Normal guibg=NONE ctermbg=NONE " Transparent background
```

## Pairing Elements
in ~/.vimrc:
```
" ...
Plug 'jiangmiao/auto-pairs'
" ...
```
## Install coc-als

- visit: https://open-vsx.org/
- search for Ada & Spark
- download
- extract
- place binary on path, eg. ~/alire/bin/

## NerdTree
in ~/.vimrc:
```
" ...
Plug 'preservim/nerdtree', {'on': 'NERDTreeToggle'}
" ...

" ctrl-b toggles nerdtree
" :help map-overview
" :help inoremap
" noremap: disable RHS and remap to LHS (non-recursive remap)
inoremap <c-b> <Esc>:NERDTreeToggle<cr> " mode: insert
										" lhs: ctrl-b
										" rhs: Esc+:NERDTreeToggle+Enter
nnoremap <c-b> <Esc>:NERDTreeToggle<cr> " mode: normal
										" lhs: ctrl-b
										" rhs: Esc+:NERDTreeToggle+Enter

" Configure nerdtree a little
let NERDTreeWinSize=32
let NERDTreeWinPos="left"
let NERDTreeShowHidden=1
let NERDTreeAutoDeleteBuffer=1
let NERDTreeAutoDeleteBuffer=1

" quit if nertree is the only remaining split: https://stackoverflow.com/questions/2066590/automatically-quit-vim-if-nerdtree-is-last-and-only-buffer

" detect Alt key properly: https://stackoverflow.com/questions/6778961/alt-key-shortcuts-not-working-on-gnome-terminal-with-vim

" Ctrl-[h,j,k,l] move around splits
map <C-j> <C-W>j
map <C-k> <C-W>k
map <C-h> <C-W>h
map <C-l> <C-W>l

" Alt-[h,j,k,l] resize splits
nnoremap <A-j> :resize +1<CR>
nnoremap <A-k> :resize -1<CR>
nnoremap <A-h> :vertical resize -1<CR>
nnoremap <A-l> :vertical resize +1<CR>
```

## Code folding with space
in ~/.vimrc:
```
" Code folding
set foldmethod=indent
nnoremap <space> za
vnoremap <space> zf
```