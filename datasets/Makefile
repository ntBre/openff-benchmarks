industry.json: download.py
	python download.py "OpenFF Industry Benchmark Season 1 v1.1" -o $@ -p

tm-supp.json: download.py
	python download.py \
"OpenFF Torsion Multiplicity Optimization Benchmarking Coverage Supplement v1.0" \
--output-file $@ --pretty-print

filtered-%.json: %.json filter.py
	python filter.py -i $< -o $@ -c .cache/$$$$

cache/%.json: %.json cache_dataset.py
	mkdir -p cache
	python cache_dataset.py -i $< -o $@
