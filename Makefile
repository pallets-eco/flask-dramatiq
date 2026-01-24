test:
	pytest -x tests/func/


PUBLISH_REMOTE=git@github.com:pallets-eco/flask-dramatiq.git
publish:
	uv build
	uv publish
	git push --follow-tags $(PUBLISH_REMOTE)
