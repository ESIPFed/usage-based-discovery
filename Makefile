.PHONY: gremlin load run dev

gremlin:
	docker run -d -p 8182:8182 --name=ubd-app-db tinkerpop/gremlin-server && sleep 10

load:
	. venv/bin/activate && python -m util.load_graph -i util/sample_data.csv -e development

run:
	. venv/bin/activate && python app_local.py

start-test:
	docker run -d -p 8183:8182 --name=ubd-test-db tinkerpop/gremlin-server && sleep 10
	. venv/bin/activate && pytest
	docker rm --force ubd-test-db

clean-test:
	docker rm --force ubd-test-db

start-app: gremlin load run

clean-app:
	docker rm --force ubd-app-db
