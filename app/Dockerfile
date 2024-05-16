FROM python:3.12.3-alpine

# get curl for healthchecks
RUN apk add --no-cache curl

# Add build dependencies
RUN apk add --no-cache gcc python3-dev musl-dev

# permissions and nonroot user for tightened security
RUN adduser -D nonroot
RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app
USER nonroot

# copy dependencies file to the container
COPY --chown=nonroot:nonroot ./requirements.txt .

# venv
ENV VIRTUAL_ENV=/home/app/venv

# python setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -r requirements.txt
RUN export FLASK_APP=main.py

# copy application files to the container
COPY --chown=nonroot:nonroot . .

CMD ["gunicorn", "-w", "3", "-t", "60", "-b", "0.0.0.0:80", "main:app"]