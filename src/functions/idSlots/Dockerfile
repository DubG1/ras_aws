FROM public.ecr.aws/lambda/python:3.12
RUN pip install \
    pillow
COPY identifySlots.py ${LAMBDA_TASK_ROOT}
CMD [ "identifySlots.lambda_handler" ]