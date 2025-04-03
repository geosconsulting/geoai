FROM osgeo/gdal:ubuntu-small-latest
LABEL authors="fabiolana"

# install pip
RUN apt-get update && apt-get -y install python3-pip --fix-missing

# set working dir
WORKDIR /app

# Install pip requirements
COPY requirements.txt /app
RUN python -m pip install -r requirements.txt

# copy all ancillary data
COPY x2030_quakes/*.py x2030_quakes/
COPY configuration_files/*.ini configuration_files/
COPY slds/*.sld slds/
COPY sqls/*.sql sqls/

# Make LOGS directory
RUN mkdir -p /app/logs

# copy main in root
COPY main.py .
COPY serve.sh .
RUN chmod +x serve.sh

#CMD ["python", "main.py"]

# EXPOSE - informs Docker that the container listens on the specified network ports at runtime
EXPOSE 5000

# ENTRYPOINT - configure a container that will run as an executable.
ENTRYPOINT ["./serve.sh"]