.PHONY: install

install:
	-mkdir ~/blackbboard
	-cp -f main.py ~/blackbboard/
	echo '~/blackbboard/main.py $*' >|~/bin/blackbboard
	chmod +x ~/bin/blackbboard
