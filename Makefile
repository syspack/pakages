SHELL = bash

.PHONY: all

all:
	black pakages/*.py pakages/utils/*.py pakages/cli/*.py pakages/handlers/*.py
