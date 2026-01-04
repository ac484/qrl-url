.PHONY: install-dev fmt lint type complexity test

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

fmt:
	black api infrastructure services repositories domain src tests

lint:
	ruff check api infrastructure services repositories domain src tests

type:
	mypy api infrastructure services repositories domain src

complexity:
	radon cc api infrastructure services repositories domain src -s -n B

test:
	pytest
