FROM public.ecr.aws/lambda/python:3.12
RUN pip install \
    opencv-python-headless \
    numpy \
    redis
COPY detectSeverity.py ${LAMBDA_TASK_ROOT}
CMD ["detectSeverity.lambda_handler"]