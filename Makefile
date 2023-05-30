.venv/venv.timestamp:
	python3 -m venv .venv
	.venv/bin/pip install wheel
	touch $@


.venv/requirements.timestamp: .venv/venv.timestamp setup.py requirements.txt
	.venv/bin/pip install --upgrade -r requirements.txt
	touch $@


.PHONY: git-attributes
git-attributes:
	git --no-pager diff --check `git log --oneline | tail -1 | cut --fields=1 --delimiter=' '`


.PHONY: lint
lint: .venv/requirements.timestamp
	.venv/bin/flake8


.PHONY: test
test: .venv/requirements.timestamp
	.venv/bin/py.test -vv --cov=geolink2oereb --cov-report term-missing:skip-covered tests


.PHONY: check
check: git-attributes lint test


.PHONY: clean
clean:
	rm -rf .venv


.PHONY: build
build: .venv/requirements.timestamp
	.venv/bin/python setup.py clean sdist bdist_wheel


.PHONY: deploy
deploy: .venv/requirements.timestamp
	.venv/bin/python setup.py clean sdist bdist_wheel upload


.PHONY: doc
doc: .venv/requirements.timestamp
	.venv/bin/sphinx-build -b html doc/source/ doc/build/html/