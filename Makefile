serve:
	uv run mkdocs serve --livereload

serve-offline:
	uv run --offline mkdocs serve --livereload

build:
	uv run mkdocs build
	find site -name "*~" -delete # delete all the emacs backup files

gh-deploy:
	uv run mkdocs gh-deploy

# open mkdocs-material source code in the editor
edit-py:
	e `uv run python -c 'import material; print(material.__file__)'`

aws-preview-deploy: build
	rsync -avz --delete site/ aws:/home/ubuntu/www/f.antocuni.eu/preview/
	echo http://f.antocuni.eu/preview/
