serve:
	uv run --with-requirements requirements.txt mkdocs serve

build:
	uv run --with-requirements requirements.txt mkdocs build

gh-deploy:
	uv run --with-requirements requirements.txt mkdocs gh-deploy
