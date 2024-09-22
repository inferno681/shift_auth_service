#!/bin/sh
apt list --installed

git config --global --add safe.directory /workspace

# oh-my-zsh theme config
if [ ! -d "~/.oh-my-zsh/custom/themes/powerlevel10k" ] ; then
    git clone --depth 1 https://github.com/romkatv/powerlevel10k.git ~/.oh-my-zsh/custom/themes/powerlevel10k
fi

# kubernetes config
if [ "$SYNC_LOCALHOST_KUBECONFIG" = "true" ] && [ -d "/usr/local/share/kube-localhost" ]; then
    mkdir -p $HOME/.kube
    cp -r /usr/local/share/kube-localhost/* $HOME/.kube
    chown -R $(id -u) $HOME/.kube
    sed -i -e "s|/Users/[a-z]\+\(/.kube/.*\)|$HOME\1|gm" $HOME/.kube/config
fi

# poetry config
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true
mkdir -p ~/.oh-my-zsh/plugins/poetry
poetry completions zsh > ~/.oh-my-zsh/plugins/poetry/_poetry

poetry install --all-extras --compile --no-root
