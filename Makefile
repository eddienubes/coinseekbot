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