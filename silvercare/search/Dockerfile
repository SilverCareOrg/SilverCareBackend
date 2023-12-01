# Use an official Solr runtime as a parent image
FROM solr:latest

# Switch to the root user
USER root

# Copy the Solr configurations from the local solr-config/new_core directory to the container
COPY solr-config/new_core /var/solr/data/new_core

# Copy the stopwords_ro.txt file from the local directory to the container
COPY stopwords_ro.txt /var/solr/data/new_core/lang/stopwords_ro.txt

# Change the ownership of the /var/solr/data/new_core directory to the solr user
RUN chown -R solr:solr /var/solr/data/new_core

# Switch back to the solr user
USER solr

# Expose the Solr port
EXPOSE 8983

# Start Solr with the custom configurations
CMD ["solr", "start", "-f"]