env:
	cd docker/dev && ./up.sh

down:
	cd docker/dev && ./down.sh
	
bot:
	export PYTHONPATH="./:./src" && python3 src/bot.py

ingest:
	export PYTHONPATH="./:./src" && python3 src/ingest.py
	
test:
	export PYTHONPATH="./:./src" && pytest 

migrate-gen:
	alembic -c src/postgres/alembic/alembic.ini revision --autogenerate
	
migrate-pg:
	alembic -c src/postgres/alembic/alembic.ini upgrade head

migrate-undo:
	alembic -c src/postgres/alembic/alembic.ini downgrade -1