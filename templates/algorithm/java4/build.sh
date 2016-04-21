#!/bin/bash

JARS="ivy dist lib"

# Build jars
ant stage $@ && \

# Assemble algorithm.zip
zip -1 -FS -r algorithm.zip $JARS

EXIT_CODE=$?

# Clean up
ant clean

exit $EXIT_CODE
