@echo off

cd /d ..

rm -rf dist
rm -rf build
rm -rf scripts/main.spec

python -m PyInstaller -F ^
--collect-all fake_useragent ^
src/webfuzz/main.py

move main.spec scripts

pause