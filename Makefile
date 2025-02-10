serve:
	uv run --with-requirements requirements.txt mkdocs serve

gh-deploy:
	uv run --with-requirements requirements.txt mkdocs gh-deploy
