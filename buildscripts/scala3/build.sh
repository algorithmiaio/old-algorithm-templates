#!/bin/bash

JARS="lib_managed lib target/scala-2.11/*.jar"

# Build jars
sbt $@ clean package && \

# Assemble algorithm.zip
zip -FS -r algorithm.zip $JARS

EXIT_CODE=$?

# Clean up
# sbt clean

exit $EXIT_CODE
