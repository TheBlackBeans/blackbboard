.PHONY: all install update dependencies pull setup

SHELL := /bin/bash

DIR = $(HOME)/.blackbboard
SHORTDIR = $(HOME)/bin
SHORTCUT = $(HOME)/bin/blackbboard
SHORTCUTUP = $(HOME)/bin/bbb-update

all: dependencies update

dependencies:
	@echo 'DEPENDENCIES'
	@echo 'Checking dependencies...'
ifeq (,$(shell which python3))
	@echo 'Installing python3 and pip3...'
	sudo apt-get install python3 python3-pip
else
	@echo 'Found python3...'
ifeq (,$(shell which pip3))
	@echo  'Installing pip3...'
	sudo apt-get install python3-pip
else
	@echo 'Found pip3...'
endif
endif
	-@python3 -c 'import pygame' >/dev/null 2>&1
ifeq (1,$(?))
	@echo 'Installing pygame...'
	sudo pip3 install pygame
else
	@echo 'Found pygame...'
endif
	@echo 'Dependecies fully installed!'

pull:
	git pull

$(DIR):
ifeq ("$(wildcard $(DIR))", "")
	@echo 'Creating the envrironment...'
	mkdir $(DIR)
endif

$(SHORTDIR):
ifeq ($(wildcard $(SHORTDIR)),)
	@echo 'Creating shortcut directory...'
	@echo "WARNING: IF THE SHORTCUT DOES NOT WORK, COSIDER ADDING $(SHORTDIR) TO YOUR PATH"
	@mkdir $(SHORTDIR)
endif
	[[ ":$(PATH)" == *":$(HOME)/bin:"* ]] || echo 'PATH=$$PATH:$$HOME/bin' >> $(HOME)/.bashrc
	. .bashrc


$(SHORTCUT):
ifeq ("$(wildcard $(SHORTCUT))", "")
	@echo 'Creating the shortcut...'
	@echo '$(DIR)/blackbboard $$*' >|$(SHORTCUT)
endif
	chmod +x $(SHORTCUT)

$(SHORTCUTUP):
ifeq ("$(wildcard $(SHORTCUTUP))", "")
	@echo 'Creating the shortcut for update...'
	@echo 'cd $(DIR);make update' >|$(SHORTCUTUP)
endif
	chmod +x $(SHORTCUTUP)


setup: $(DIR) $(SHORTDIR) $(SHORTCUT) $(SHORTCUTUP)
	@echo 'Setup done!'

install: $(shell find * -type f) setup
	@echo 'INSTALL'
	@echo 'Copying to environment...'
	-cp -rf * $(DIR)/
	-cp -rf .git $(DIR)/.git
	@echo 'Bounding to shortcut...'
	-mv $(DIR)/main.py $(DIR)/blackbboard
	@echo 'Install done!'

update: pull install
	@echo 'Update done!'
