# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory inside the container
WORKDIR /var/task

# Copy the necessary files into container
COPY ./src /var/task/src
COPY requirements.txt /var/task/
COPY ./info /var/task/info
COPY lambda_handler.py /var/task/


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Execute code
CMD ["lambda_handler.lambda_handler"]
