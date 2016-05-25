#!/usr/bin/env bash

set -e

# Base on https://github.com/drKraken/dev-setup/blob/master/setup.sh
# Script.sh
# Simple and nice script that
# help make your machine ready
# for fun

# declare variables here
SCRIPT_NAME="setup.sh"
SCRIPT_VERSION="0.1"
SCRIPT_FLAG=$1

DEFAULT_USER_NAME=hiepsimu
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#is_user_exists() {
#    ret=1
#    getent passwd $1 >/dev/null 2>&1 && ret=0
#    return $ret
#}
#
## Check user
#ret=false
#getent passwd $1 >/dev/null 2>&1 && ret=true
#
#if id -u "$DEFAULT_USER_NAME" >/dev/null 2>&1; then
#        echo "user exists"
#else
#        echo "user does not exist"
#fi

function install_docker {
  # Install docker (apt-get update will be called). If you don't need docker, `apt-get update` has to be executed first
  if [ ! -e "/usr/bin/docker" ]; then
      echo Install docker
      curl -SL "http://get.docker.com" | sh
      sudo usermod -aG docker $DEFAULT_USER_NAME
      sudo ln -sf /usr/bin/docker /usr/local/bin/d
  fi

  if [ ! -e "/usr/local/bin/docker-compose" ]; then
    echo Install docker-compose
    sudo pip install docker-compose
    sudo ln -sf /usr/local/bin/docker-compose /usr/local/bin/dc
  fi
}

function install_common {
  # Setup packages
  sudo apt-get update

  COMMON_PACKAGE=""
  COMMON_PACKAGE="$COMMON_PACKAGE xubuntu-desktop git terminator"
  COMMON_PACKAGE="$COMMON_PACKAGE htop"
  COMMON_PACKAGE="$COMMON_PACKAGE python-pip"
  # for coffee
  COMMON_PACKAGE="$COMMON_PACKAGE entr libpq-dev"
  # for subfind
  COMMON_PACKAGE="$COMMON_PACKAGE unrar libxml2-dev libxslt1-dev"

  sudo apt-get install -qqy $COMMON_PACKAGE

  # Upgrade pip
  sudo pip install --upgrade pip
}

function list_package {
  echo Packages contain \'$1\'
  dpkg --get-selections | grep -v deinstall | awk '{print $1}' | grep $1
}

function remove_package {
  echo Remove package contain \'$1\'
  dpkg --get-selections | grep -v deinstall | awk '{print $1}' | grep $1 | awk '{print "sudo apt-get purge -qqy "$1}' | bash
}

function remove_common {
  remove_package firefox
  remove_package libreoffice
  remove_package thunderbird
  remove_package empathy
  remove_package pidgin
#  remove_package remmina
  remove_package webbrowser-app
  remove_package gmusic
  remove_package parole
}

# Setup confd
function install_confd {
  if [ ! -e /usr/bin/confd ]; then
      curl -SL "https://github.com/kelseyhightower/confd/releases/download/v0.10.0/confd-0.10.0-linux-amd64" -o /usr/bin/confd
      chmod +x /usr/bin/confd
  fi
}

# Install PyCharm
function install_pycharm {
  PYCHARM_VERSION="2016.1.2"

  if [ ! -e pycharm-community-$PYCHARM_VERSION ]; then
      if [ ! -e /opt/pycharm.tar.gz ]; then
          curl -SL "https://download.jetbrains.com/python/pycharm-community-$PYCHARM_VERSION.tar.gz" -o /opt/pycharm.tar.gz
      fi
      cd /opt
      tar xzf pycharm.tar.gz

      # Create launcher
      cat << EOF > /home/$DEFAULT_USER_NAME/Desktop/PyCharm.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=PyCharm
Comment=
Exec=/opt/pycharm-community-$PYCHARM_VERSION/bin/pycharm.sh
Icon=/opt/pycharm-community-$PYCHARM_VERSION/bin/pycharm.png
Path=
Terminal=false
StartupNotify=false
EOF

      chown $DEFAULT_USER_NAME:$DEFAULT_USER_NAME /home/$DEFAULT_USER_NAME/Desktop/PyCharm.desktop
      chmod +x /home/$DEFAULT_USER_NAME/Desktop/PyCharm.desktop
      rm pycharm.tar.gz
  fi
}

cd $DIR

function install_teamviewer {
  # Install TeamViewer
  curl -SL "http://download.teamviewer.com/download/teamviewer_amd64.deb" -o "/tmp/teamviewer.deb"
  dpkg -i /tmp/teamviewer.deb
  apt-get install -f -y
}

# chromium
#function install_chromium {
#  cd $(dirname $0)
#
#  LASTCHANGE_URL="https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2FLAST_CHANGE?alt=media"
#
#  REVISION=$(curl -s -S $LASTCHANGE_URL)
#
#  echo "latest revision is $REVISION"
#
#  if [ -d $REVISION ] ; then
#    echo "already have latest version"
#    exit
#  fi
#}

# chrome
function install_chrome {
  # Base on http://www.ubuntuupdates.org/ppa/google_chrome?dist=stable
  wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

  sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

  sudo apt-get update -qq
  sudo apt-get install -qqy google-chrome-stable
}

# virtualbox

# robomongo

# sublime text
function install_sublime_text {
  # From https://gist.github.com/simonewebdesign/8507139
  # Detect the architecture
  if [ "$(uname -m)" = "x86_64" ]; then
    ARCHITECTURE="x64"
  else
    ARCHITECTURE="x32"
  fi

  # Fetch the latest build version number (thanks daveol)
  BUILD=$(echo $(curl http://www.sublimetext.com/3) | sed -rn "s#.*The latest build is ([0-9]+)..*#\1#p")

  URL="https://download.sublimetext.com/sublime_text_3_build_{$BUILD}_{$ARCHITECTURE}.tar.bz2"
  INSTALLATION_DIR="/opt/sublime_text"

  # Download the tarball, unpack and install
  curl -o $HOME/st3.tar.bz2 $URL
  if tar -xf $HOME/st3.tar.bz2 --directory=$HOME; then
    # Remove the installation folder and the symlink, they might already exist
    sudo rm -rf $INSTALLATION_DIR /bin/subl
    sudo mv $HOME/sublime_text_3 $INSTALLATION_DIR
    sudo ln -s $INSTALLATION_DIR/sublime_text /bin/subl
  fi
  rm $HOME/st3.tar.bz2
  mkdir -p "$INSTALLATION_DIR/Installed Packages/"

  # Package Control - The Sublime Text Package Manager: https://sublime.wbond.net
  curl -o $HOME/Package\ Control.sublime-package -k https://sublime.wbond.net/Package%20Control.sublime-package
  sudo mv $HOME/Package\ Control.sublime-package "$INSTALLATION_DIR/Installed Packages/"

  # Add to applications list (thanks 4ndrej)
  sudo ln -s $INSTALLATION_DIR/sublime_text.desktop /usr/share/applications/sublime_text.desktop

  # Set the icon (thanks gcaracuel)
  sudo sed -i.bak 's/Icon=sublime-text/Icon=\/opt\/sublime_text\/Icon\/128x128\/sublime-text.png/g' /usr/share/applications/sublime_text.desktop

  echo ""
  echo "Sublime Text 3 installed successfully!"
  echo "Run with: subl"
}

# vagrant

# Install theme paper
function install_theme_paper {
  sudo add-apt-repository -y ppa:snwh/pulp
  sudo apt-get update -qq
  sudo apt-get install -qqy paper-gtk-theme
  sudo apt-get install -qqy paper-icon-theme

  echo "Installed paper theme. Open Window Manager to change theme"
}

function install_nuclide {
  wget https://atom.io/download/deb
  mv deb atom-amd64.deb
  sudo dpkg -i atom-amd64.deb

  apm install nuclide

  sudo rm /home/$DEFAULT_USER_NAME/.atom -rf

  rm atom-amd64.deb -f
}

function install_nodejs {
  curl -sL https://deb.nodesource.com/setup_5.x | sudo -E bash -
  sudo apt-get install -y nodejs

  curl -sSL https://www.npmjs.org/install.sh | sh
}

function install_plex {
  curl -sSL https://downloads.plex.tv/plex-media-server/0.9.16.4.1911-ee6e505/plexmediaserver_0.9.16.4.1911-ee6e505_amd64.deb -o plex.deb

  sudo dpkg -i plex.deb
}

function install_fish {
  sudo apt-add-repository -y ppa:fish-shell/release-2
  sudo apt-get update -qq
  sudo apt-get install -qqy fish

  chsh -s /usr/bin/fish

  sudo chsh -s /usr/bin/fish
}

# Call confd to override config

#install_docker
#install_chrome

#install_sublime_text
#install_common
#remove_common

#install_theme_paper
#install_nuclide
#list_package parole

#install_nodejs

#install_plex
#install_pycharm

install_fish

#sudo apt-get autoremove -y

