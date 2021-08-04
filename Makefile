SHELL := /bin/bash

.PHONY: run-app-db run-test-db load-app-db run-app run-test test app clean-test clean-app clean

run-app-db:
	docker run -d -p 8183:8182 --name=ubd-app-db tinkerpop/gremlin-server && sleep 5

run-test-db:
	docker run -d -p 8182:8182 --name=ubd-test-db tinkerpop/gremlin-server && sleep 5

load-app-db:
	. venv/bin/activate && python -m util.load_graph -i util/sample_data.csv -e development

run-app:
	. venv/bin/activate && python app_local.py

run-test:
	. venv/bin/activate && pytest -v -rP

test:
	if [ ! "$$(docker ps -a | grep ubd-test-db)" ]; then \
		make run-test-db; \
	fi
	make run-test

app:
	if [ ! "$$(docker ps -a | grep ubd-app-db)" ]; then \
		make run-app-db; \
		make load-app-db; \
	fi
	make run-app

clean-test:
	docker rm --force ubd-test-db

clean-app:
	docker rm --force ubd-app-db

clean: clean-test clean-app
