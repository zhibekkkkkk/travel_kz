PY=python3
VENV=. .venv/bin/activate

all: setup collect report

setup:
	python3 -m venv .venv && ${VENV} && pip install -r python/requirements.txt

collect:
	${VENV} && OMP_NUM_THREADS=1 ${PY} -m python.collect_all

report:
	cd go && go mod tidy && go run main.go

clean:
	rm -rf data/raw/*.json data/out/*.json data/out/*.csv data/out/*.md
