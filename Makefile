VERSION = 0.9.25
PACKAGE = wagtail-airspace

#======================================================================

clean:
	rm -rf *.tar.gz dist *.egg-info *.rpm
	find . -name "*.pyc" -exec rm '{}' ';'

version:
	@echo ${VERSION}
