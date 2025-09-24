serve:
	uv run --with-requirements requirements.txt mkdocs serve --livereload

serve-offline:
	uv run --offline --with-requirements requirements.txt mkdocs serve --livereload

build:
	uv run --with-requirements requirements.txt mkdocs build
	find site -name "*~" -delete # delete all the emacs backup files

gh-deploy:
	uv run --with-requirements requirements.txt mkdocs gh-deploy

# open mkdocs-material source code in the editor
edit-py:
	e `uv run --with-requirements requirements.txt python -c 'import material; print(material.__file__)'`

aws-preview-deploy: build
	rsync -avz --delete site/ aws:/home/ubuntu/www/f.antocuni.eu/preview/
	echo http://f.antocuni.eu/preview/
