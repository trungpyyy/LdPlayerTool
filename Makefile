.PHONY: build

build:
	pyinstaller --noconsole --onefile main.py \
	--add-data "images;images" \
	--add-data "adb;adb" \
	--add-data "data;data" \
	--add-data "logs;logs"
	cp ./dist/main.exe ./
