# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.9


COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# COPY ./info ./info
COPY ./src ${LAMBDA_TASK_ROOT}/src

COPY ./lambda_handler.py ./ticketsforgood.txt ${LAMBDA_TASK_ROOT}


CMD ["lambda_handler.lambda_handler"]
