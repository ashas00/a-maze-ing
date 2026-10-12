PYTHON = python3
VENV = .venv
PY = $(VENV)/bin/python
CONFIG = config.txt

.PHONY: install run debug clean fclean lint lint-strict

install:
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install --upgrade pip flake8 mypy

run:
	$(PY) a_maze_ing.py $(CONFIG)

debug:
	$(PY) -m pdb a_maze_ing.py $(CONFIG)

clean:
	rm -rf __pycache__ .mypy_cache

fclean: clean
	rm -rf $(VENV)

lint:
	$(PY) -m flake8 --exclude=$(VENV) .
	$(PY) -m mypy . --exclude '(^|/)$(VENV)/' --warn-return-any \
		--warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PY) -m flake8 --exclude=$(VENV) .
	$(PY) -m mypy . --exclude '(^|/)$(VENV)/' --strict
