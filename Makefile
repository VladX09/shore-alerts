.PHONY: format_code, check_code compose help

include secrets.env
export

# If the first argument is "compose"...
ifeq (compose,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments
  COMPOSE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # and turn them into do-nothing targets
  $(eval $(COMPOSE_ARGS):;@:)
endif

## format_code:              Apply code foramtters
format_code:
	isort --settings-file .isort.cfg .
	black --config .black.toml .

## check_code:               Run linters and tests
check_code:
	isort -c --diff --settings-file .isort.cfg .
	black --config .black.toml --check .
	flake8 --config .flake8 .

## compose:                  Perform docker compose operation
compose:
	docker compose $(COMPOSE_ARGS)

help:
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)
