# Spark standalone node (master / worker) with Delta Lake + Kafka connector.
FROM apache/spark:3.5.3-scala2.12-java17-python3-ubuntu

USER root

ARG DELTA_VERSION=3.2.1
ARG ICEBERG_VERSION=1.7.2
ARG SPARK_VERSION=3.5.3
ARG SCALA_BINARY=2.12
ARG KAFKA_CLIENTS=3.4.1
ARG COMMONS_POOL2=2.11.1

ENV SPARK_HOME=/opt/spark

# Bake the connector jars into $SPARK_HOME/jars so students never need --packages
# (works fully offline once the image is built). Both Delta Lake AND Apache
# Iceberg are bundled so students can pick either table format.
RUN set -eux; \
    cd "$SPARK_HOME/jars"; \
    MVN=https://repo1.maven.org/maven2; \
    curl -fSL "$MVN/io/delta/delta-spark_${SCALA_BINARY}/${DELTA_VERSION}/delta-spark_${SCALA_BINARY}-${DELTA_VERSION}.jar" -o "delta-spark_${SCALA_BINARY}-${DELTA_VERSION}.jar"; \
    curl -fSL "$MVN/io/delta/delta-storage/${DELTA_VERSION}/delta-storage-${DELTA_VERSION}.jar" -o "delta-storage-${DELTA_VERSION}.jar"; \
    curl -fSL "$MVN/org/apache/iceberg/iceberg-spark-runtime-3.5_${SCALA_BINARY}/${ICEBERG_VERSION}/iceberg-spark-runtime-3.5_${SCALA_BINARY}-${ICEBERG_VERSION}.jar" -o "iceberg-spark-runtime-3.5_${SCALA_BINARY}-${ICEBERG_VERSION}.jar"; \
    curl -fSL "$MVN/org/apache/spark/spark-sql-kafka-0-10_${SCALA_BINARY}/${SPARK_VERSION}/spark-sql-kafka-0-10_${SCALA_BINARY}-${SPARK_VERSION}.jar" -o "spark-sql-kafka-0-10_${SCALA_BINARY}-${SPARK_VERSION}.jar"; \
    curl -fSL "$MVN/org/apache/spark/spark-token-provider-kafka-0-10_${SCALA_BINARY}/${SPARK_VERSION}/spark-token-provider-kafka-0-10_${SCALA_BINARY}-${SPARK_VERSION}.jar" -o "spark-token-provider-kafka-0-10_${SCALA_BINARY}-${SPARK_VERSION}.jar"; \
    curl -fSL "$MVN/org/apache/kafka/kafka-clients/${KAFKA_CLIENTS}/kafka-clients-${KAFKA_CLIENTS}.jar" -o "kafka-clients-${KAFKA_CLIENTS}.jar"; \
    curl -fSL "$MVN/org/apache/commons/commons-pool2/${COMMONS_POOL2}/commons-pool2-${COMMONS_POOL2}.jar" -o "commons-pool2-${COMMONS_POOL2}.jar"

# Enable the Delta + Iceberg catalogs/extensions for every SparkSession.
COPY spark-defaults.conf $SPARK_HOME/conf/spark-defaults.conf

ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip
