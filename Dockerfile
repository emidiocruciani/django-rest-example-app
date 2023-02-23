FROM python:alpine AS base

# Set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install needed packages
RUN apk add zip unzip curl bash su-exec supervisor

# Setup bash
RUN sed -i 's/bin\/ash/bin\/bash/g' /etc/passwd

# Configure supervisor (base)
RUN mkdir -p /etc/supervisor.d/
RUN mkdir -p /var/log/supervisor


FROM base AS development

# Development variables
ARG WWWUSER=1000
ARG WWWGROUP=1000

ENV WWWUSER=$WWWUSER
ENV WWWGROUP=$WWWGROUP

# Add local development user
RUN addgroup -S -g $WWWGROUP python-dev
RUN adduser -D -S -s /bin/bash -G python-dev -u $WWWUSER python-dev

# Configure supervisor (development)
COPY ./docker/dev/app/supervisord.ini /etc/supervisor.d/supervisord.ini

# Load entrypoint script
COPY ./docker/dev/app/start-container /usr/local/bin/start-container
RUN chmod +x /usr/local/bin/start-container

# Make staticfiles dir
RUN mkdir /app/staticfiles
RUN chown -R $WWWUSER:$WWWGROUP /app/staticfiles

# install dependencies
RUN apk update && apk add libpq gettext && pip install --upgrade pip

# Copy requirements file
COPY ./docker/dev/app/requirements.txt .

# Install requirements with virtual deps to reduce image size
RUN apk --virtual .build-deps add postgresql-dev gcc python3-dev musl-dev \
&& pip install -r requirements.txt \
&&  apk del .build-deps

# Expose port
EXPOSE 8000

# Set container entrypoint
CMD ["start-container"]


FROM base AS production

# Configure supervisor (development)
COPY ./docker/prod/app/supervisord.ini /etc/supervisor.d/supervisord.ini

# Load entrypoint script
COPY ./docker/prod/app/start-container /usr/local/bin/start-container
RUN chmod +x /usr/local/bin/start-container

# install dependencies
RUN apk update && apk add libpq gettext && pip install --upgrade pip

# Copy requirements file
COPY ./docker/prod/app/requirements.txt .

# Install requirements with virtual deps to reduce image size
RUN apk --virtual .build-deps add postgresql-dev gcc python3-dev musl-dev \
&& pip install -r requirements.txt \
&& apk del .build-deps

# Copy all (see .dockerignore for exceptions)
COPY ./source /app/
RUN chown -R www-data:www-data /app

# Expose port
EXPOSE 8000

# Set container entrypoint
CMD ["start-container"]
