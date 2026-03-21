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

preview-deploy:
	sed 's/draft: false/draft: true/' mkdocs.yml > mkdocs-preview.yml
	uv run mkdocs build -f mkdocs-preview.yml
	find site -name "*~" -delete
	rm mkdocs-preview.yml
	wrangler deploy --name preview-antocuni-eu --assets site/ --compatibility-date 2024-09-23
	echo https://preview.antocuni.eu
