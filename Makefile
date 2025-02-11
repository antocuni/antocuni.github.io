serve:
	uv run --with-requirements requirements.txt mkdocs serve

build:
	uv run --with-requirements requirements.txt mkdocs build
	find site -name "*~" -delete # delete all the emacs backup files

gh-deploy:
	uv run --with-requirements requirements.txt mkdocs gh-deploy


aws-deploy: build
	rsync -avz --delete site/ aws:/home/ubuntu/www/antocuni.eu/blog
