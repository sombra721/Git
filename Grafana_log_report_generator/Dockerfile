From aaron465/matplotlib

COPY perf.py /
COPY whisper.py /

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y install python-tk
RUN pip install -U pip
RUN pip install fpdf 

EXPOSE 28555 
CMD ["python", "./perf.py"]
