DBLATEX_OPTS := -bxetex -P doc.publisher.show=0 -P latex.output.revhistory=0
all: gcodetools-ru.pdf gcodetools-ru.html gcodetools-ru.odt

%.pdf: %.asciidoc
	a2x -f pdf -v --dblatex-opts="$(DBLATEX_OPTS)" $<

%.html: %.asciidoc
	a2x -f xhtml -v --dblatex-opts="$(DBLATEX_OPTS)" $<
	
%.odt: %.asciidoc
	a2x -f odt -v --dblatex-opts="$(DBLATEX_OPTS)" $<
