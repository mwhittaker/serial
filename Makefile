default: test

.PHONY: test
test:
	# doc tests
	python serial.py
	python action.py
	# unit tests
	@for p in *_test.py; do \
		echo $$p; \
		python $$p || exit 1; \
		echo ""; \
	done
	# tex
	pdflatex exercises.tex

.PHONY: clean
clean:
	rm -f *.pyc
	rm -f exercise[0-9]*.tex
	rm -f short.tex
	rm -f tables.tex
	rm -f conflict-graph-*.pdf
	rm -f *.pdf
	rm -f *.log
	rm -f *.aux
