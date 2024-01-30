FROM public.ecr.aws/lambda/python:3.12
RUN pip install \
    pillow \
    numpy==1.26.2 \
    redis
COPY customRoadDetection.py ${LAMBDA_TASK_ROOT}
CMD ["customRoadDetection.lambda_handler"]