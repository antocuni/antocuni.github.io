serve:
	uv run --with-requirements requirements.txt --with-editable ./mkdocs_antocuni mkdocs serve --livereload

serve-offline:
	uv run --offline --with-requirements requirements.txt --with-editable ./mkdocs_antocuni mkdocs serve --livereload

build:
	uv run --with-requirements requirements.txt --with-editable ./mkdocs_antocuni mkdocs build
	find site -name "*~" -delete # delete all the emacs backup files

gh-deploy:
	uv run --with-requirements requirements.txt --with-editable ./mkdocs_antocuni mkdocs gh-deploy

# open mkdocs-material source code in the editor
edit-py:
	e `uv run --with-requirements requirements.txt python -c 'import material; print(material.__file__)'`

aws-preview-deploy: build
	rsync -avz --delete site/ aws:/home/ubuntu/www/f.antocuni.eu/preview/
	echo http://f.antocuni.eu/preview/
