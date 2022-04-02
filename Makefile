.PHONY: format_code, check_code down up help
include secrets.env
export

## format_code:              Apply code foramtters
format_code:
	isort --settings-file .isort.cfg .
	black --config .black.toml .

## check_code:               Run linters and tests
check_code:
	isort -c --diff --settings-file .isort.cfg .
	black --config .black.toml --check .
	flake8 --config .flake8 .

## down:                     Down containers
down:
	docker compose down

## up:                       Up containers
up:
	docker compose up -d

help:
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)
