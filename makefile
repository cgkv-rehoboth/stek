APP="./app"
SCRIPTS="$(APP)/scripts"
NPM_BIN=$(shell npm bin)

all:
	$(NPM_BIN)/grunt

mkenv:
	pyvenv-3.4 .virtualenv

install:
	@echo ">> trying to install compass"
	-gem install compass
	@echo ">> trying to install client deps"
	npm install
	@echo ">> installing server dependencies"
	test -d .virtualenv || ${MAKE} mkenv
	. .virtualenv/bin/activate; pip install -r requirements
