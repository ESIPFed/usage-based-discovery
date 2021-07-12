.PHONY: gremlin load run dev

gremlin:
	docker run -d -p 8182:8182 tinkerpop/gremlin-server && sleep 10

load:
	. venv/bin/activate && python -m util.load_graph -i util/sample_data.csv -e development

run:
	. venv/bin/activate && python app_local.py

test:
	. venv/bin/activate && pytest

dev: gremlin load run
