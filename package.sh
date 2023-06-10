#!/bin/sh
[ -e package ] && rm -r package
mkdir -p package/opt
mkdir -p package/usr/share/applications
mkdir -p package/usr/share/icons/hicolor/scalable/apps

cp -r dist/alinka package/opt/alinka
cp statics/alinka.svg package/usr/share/icons/hicolor/scalable/apps/alinka.svg
cp alinka.desktop package/usr/share/applications

find package/opt/alinka -type f -exec chmod 644 -- {} +
find package/opt/alinka -type d -exec chmod 755 -- {} +
find package/usr/share -type f -exec chmod 644 -- {} +
chmod +x package/opt/alinka/alinka
