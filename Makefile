.PHONY: help init_linters lint


help: ## Commands
	@echo "Please use 'make <target>' where <target> is one of:"
	@awk -F ':|##' '/^[a-zA-Z\-_0-9]+:/ && !/^[ \t]*all:/ { printf "\t\033[36m%-30s\033[0m %s\n", $$1, $$3 }' $(MAKEFILE_LIST)

init_linters: ## Install pre-commit hooks
	@pre-commit install


lint: init_linters ## Run linting
	@pre-commit run -a
