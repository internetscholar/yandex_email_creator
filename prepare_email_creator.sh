#!/usr/bin/env bash

# tbselenium does not work with Tor Browser 8.0. Had to downgrade to 7.5.6
# this code assumes that Tor Browser is at $HOME_DIR/tor-browser_en-US
wget -P ~ https://dist.torproject.org/torbrowser/7.5.6/tor-browser-linux64-7.5.6_en-US.tar.xz
tar -xvJf ~/tor-browser-linux64-7.5.6_en-US.tar.xz -C ~
rm ~/tor-browser-linux64-7.5.6_en-US.tar.xz

# tbselenium requires geckodriver 0.17.0. Ref: https://github.com/webfp/tor-browser-selenium#installation
wget -P ~ https://github.com/mozilla/geckodriver/releases/download/v0.17.0/geckodriver-v0.17.0-linux64.tar.gz
tar -xzf ~/geckodriver-v0.17.0-linux64.tar.gz -C ~
rm ~/geckodriver-v0.17.0-linux64.tar.gz

sudo mv ~/geckodriver /usr/local/bin/