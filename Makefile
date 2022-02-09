.PHONY: all
VIRTUAL_ENV=.venv

env: # create the virtual environment to avoid polluting global site-packages
	python3 -m venv ${VIRTUAL_ENV}

install: # install requirements into virtual environment
	@PATH=$(VIRTUAL_ENV)/bin:$(PATH); pip3 install -U pip; pip3 install -r requirements.txt;

setup: env install

test: 
	@PATH=$(VIRTUAL_ENV)/bin:$(PATH); pytest -v --disable-warnings

lint: 
	@PATH=$(VIRTUAL_ENV)/bin:$(PATH); flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.venv