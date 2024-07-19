industry.json: download.py
	python download.py "OpenFF Industry Benchmark Season 1 v1.1" -o $@ -p

filtered-industry.json: industry.json
	python filter.py -i $< -o $@
