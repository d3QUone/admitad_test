#!/bin/sh
VERBOSE=1

test:
	nosetests --verbosity $(VERBOSE)

coverage:
	coverage run --source $(shell pwd) -m nose --verbosity $(VERBOSE)

coverage_report:
	coverage html
	coverage report
