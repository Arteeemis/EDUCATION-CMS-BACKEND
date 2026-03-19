FROM python

WORKDIR /education_cms_backend

COPY req.txt .

RUN pip install --upgrade pip
RUN pip install -r req.txt

COPY education_cms_backend/ .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]