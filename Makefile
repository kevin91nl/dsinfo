build:
	docker build . -t kevin91nl/dsinfo
run:
	docker run kevin91nl/dsinfo
local:
	python run.py --path ../data
