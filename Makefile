.PHONY: install update

update:
	-git pull

install: update
	-mkdir ~/blackbboard
	-cp -rf * ~/blackbboard/
	-mv ~/blackbboard/main.py ~/blackbboard/blackbboard
	echo '~/blackbboard/blackbboard $*' >|~/bin/blackbboard
	chmod +x ~/bin/blackbboard
