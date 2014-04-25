OUTPUT = tests.xml

all: $(OUTPUT)

$(OUTPUT): btts.xml btts-*.xml btts*.xsl
	java -jar /usr/share/java/saxon.jar -a:on -s:$< -t -xi:on -o:$@

.PHONY: run
run: $(OUTPUT)
	@select tc in $(shell make list); \
	do \
		ofile="test-output-$$(date +%FT%T).xml"; \
		testrunner-lite -f $(OUTPUT) -o "$${ofile}" -l "testcase=$${tc}"; \
		echo "Output saved to $${ofile}"; \
		break; \
	done

.PHONY: list
list: $(OUTPUT)
	@xmllint $(OUTPUT) --xpath '//case/@name' |sed 's/ name="\([^"]*\)"/\1\n/g'
