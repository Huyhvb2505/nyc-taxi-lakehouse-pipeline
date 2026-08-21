# Airflow with a bundled spark-submit (via the pyspark pip package) + the Spark
# provider, so SparkSubmitOperator can submit to the standalone cluster.
# Delta Lake + Kafka connector jars are baked into the client too.
FROM apache/airflow:2.10.3-python3.11

ARG DELTA_VERSION=3.2.1
ARG ICEBERG_VERSION=1.7.2
ARG SPARK_VERSION=3.5.3
ARG SCALA_BINARY=2.12
ARG KAFKA_CLIENTS=3.4.1
ARG COMMONS_POOL2=2.11.1

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps curl \
 && rm -rf /var/lib/apt/lists/* \
 && ln -s "$(dirname "$(dirname "$(readlink -f "$(which java)")")")" /opt/java
ENV JAVA_HOME=/opt/java

USER airflow
RUN pip install --no-cache-dir "apache-airflow-providers-apache-spark==4.11.0" \
 && pip install --no-cache-dir "pyspark==${SPARK_VERSION}"

# pyspark pip install => this is our SPARK_HOME (contains bin/spark-submit + jars)
ENV SPARK_HOME=/home/airflow/.local/lib/python3.11/site-packages/pyspark
ENV PATH=$SPARK_HOME/bin:$PATH

USER root
RUN set -eux; \
    mkdir -p "$SPARK_HOME/conf"; \
    cd "$SPARK_HOME/jars"; \
    MVN=https://repo1.maven.org/maven2; \
    curl -fSL "$MVN/io/delta/delta-spark_${SCALA_BINARY}/${DELTA_VERSION}/delta-spark_${SCALA_BINARY}-${DELTA_VERSION}.jar" -o "delta-spark_${SCALA_BINARY}-${DELTA_VERSION}.jar"; \
    curl -fSL "$MVN/io/delta/delta-storage/${DELTA_VERSION}/delta-storage-${DELTA_VERSION}.jar" -o "delta-storage-${DELTA_VERSION}.jar"; \
    curl -fSL "$MVN/org/apache/iceberg/iceberg-spark-runtime-3.5_${SCALA_BINARY}/${ICEBERG_VERSION}/iceberg-spark-runtime-3.5_${SCALA_BINARY}-${ICEBERG_VERSION}.jar" -o "iceberg-spark-runtime-3.5_${SCALA_BINARY}-${ICEBERG_VERSION}.jar"; \
    curl -fSL "$MVN/org/apache/spark/spark-sql-kafka-0-10_${SCALA_BINARY}/${SPARK_VERSION}/spark-sql-kafka-0-10_${SCALA_BINARY}-${SPARK_VERSION}.jar" -o "spark-sql-kafka-0-10_${SCALA_BINARY}-${SPARK_VERSION}.jar"; \
    curl -fSL "$MVN/org/apache/spark/spark-token-provider-kafka-0-10_${SCALA_BINARY}/${SPARK_VERSION}/spark-token-provider-kafka-0-10_${SCALA_BINARY}-${SPARK_VERSION}.jar" -o "spark-token-provider-kafka-0-10_${SCALA_BINARY}-${SPARK_VERSION}.jar"; \
    curl -fSL "$MVN/org/apache/kafka/kafka-clients/${KAFKA_CLIENTS}/kafka-clients-${KAFKA_CLIENTS}.jar" -o "kafka-clients-${KAFKA_CLIENTS}.jar"; \
    curl -fSL "$MVN/org/apache/commons/commons-pool2/${COMMONS_POOL2}/commons-pool2-${COMMONS_POOL2}.jar" -o "commons-pool2-${COMMONS_POOL2}.jar"

COPY spark-defaults.conf $SPARK_HOME/conf/spark-defaults.conf

USER airflow
