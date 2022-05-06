SHELL := /bin/bash

.PHONY: run-db run-test-db load-db run-app run-test test app clean-test clean-app clean build-docker run-docker db

run-db:
	docker run -d -p 8183:8182 --name=ubd-app-db tinkerpop/gremlin-server && sleep 5

run-test-db:
	docker run -d -p 8182:8182 --name=ubd-test-db tinkerpop/gremlin-server && sleep 5

load-db:
	. venv/bin/activate && python -m util.load_graph -i util/sample_data.csv -e development

build-docker:
	docker build -t ubd .

run-app:
	. venv/bin/activate && FLASK_ENV=development python app.py

run-docker:
	docker rm --force ubd-app
	docker run -d -p 5000:5000 -e IS_DOCKER=true --name=ubd-app ubd

run-test:
	. venv/bin/activate && pytest -vv -rP

test:
	if [ ! "$$(docker ps -a | grep ubd-test-db)" ]; then \
		make run-test-db; \
	fi
	make run-test
	make clean-test

db:
	if [ ! "$$(docker ps -a | grep ubd-app-db)" ]; then \
		make run-db; \
		make load-db; \
	fi

docker:
	make db
	make run-docker

app:
	make db
	make run-app

clean-test:
	docker rm --force ubd-test-db

clean-app:
	docker rm --force ubd-app
	docker rm --force ubd-app-db

clean-db:
	docker rm --force ubd-app-db

clean: clean-test clean-app
