# About

This repo is to store tips, settings for my dev environment.

# Change default git editor to vim

Nano is good, however, press Ctrl+X is harder than `:wq`

    git config --global core.editor "vim"

# React Native

Start react

    react-native start

    adb reverse tcp:8081 tcp:8081

# Android debug wifi

Connect device via USB and make sure debugging is working.

    adb tcpip 5555
    adb connect <DEVICE_IP_ADDRESS>:5555

Disconnect USB and proceed with wireless debugging.

    adb -s <DEVICE_IP_ADDRESS>:5555 usb

to switch back when done.

# Zookeeper

    sudo docker run -d -p 2818:2818 --name=zookeeper jplock/zookeeper
