FROM continuumio/miniconda3


RUN mkdir /tmp/cdqforcelayout
COPY dist/*.whl /tmp/cdqforcelayout

RUN /opt/conda/bin/pip install /tmp/cdqforcelayout/cdqforcelayout*whl

RUN rm -rf /tmp/cdqforcelayout


ENTRYPOINT ["/opt/conda/bin/cdqforcelayoutcmd.py"]
CMD ["--help"]
