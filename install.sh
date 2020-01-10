#!/usr/bin/bash
sed -i '/axe=/d' ~/.zshrc
echo 'alias axe="~/.axe/axe"' >> ~/.zshrc
