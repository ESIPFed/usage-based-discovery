.PHONY: gremlin-db load-app run-app start-test clean-test start-app clean-app clean-all

gremlin-db:
	docker run -d -p 8182:8182 --name=ubd-app-db tinkerpop/gremlin-server && sleep 10

load-app:
	. venv/bin/activate && python -m util.load_graph -i util/sample_data.csv -e development

run-app:
	. venv/bin/activate && python app_local.py

start-test:
	docker run -d -p 8183:8182 --name=ubd-test-db tinkerpop/gremlin-server && sleep 10
	. venv/bin/activate && pytest -v -rP
	docker rm --force ubd-test-db

clean-test:
	docker rm --force ubd-test-db

start-app: gremlin-db load-app run-app

clean-app:
	docker rm --force ubd-app-db

clean-all:
	docker rm --force ubd-app-db
	docker rm --force ubd-test-db
