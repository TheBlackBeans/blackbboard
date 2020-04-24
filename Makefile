.PHONY: install

install:
	-mkdir ~/blackbboard
	-cp -rf * ~/blackbboard/
	echo '~/blackbboard/main.py $*' >|~/bin/blackbboard
	chmod +x ~/bin/blackbboard
