test:
	pytest -x tests/func/


PUBLISH_REMOTE=git@gitlab.com:bersace/flask-dramatiq.git
publish:
	poetry build
	poetry publish
	git push --follow-tags $(PUBLISH_REMOTE)
