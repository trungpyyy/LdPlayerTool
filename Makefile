.PHONY: build

build:
	pyinstaller --windowed --onefile main.py \
	--add-data "images;images" \
	--add-data "adb;adb" \
	--add-data "data;data" \
	--add-data "logs;logs"
	cp ./dist/main.exe ./
