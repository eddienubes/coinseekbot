env:
	cd docker/dev && ./up.sh
	
bot:
	export PYTHONPATH="./:./src" && python3 src/bot.py

ingest:
	export PYTHONPATH="./:./src" && python3 src/ingest.py