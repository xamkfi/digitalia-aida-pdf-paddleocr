FROM python:3.9
WORKDIR /app/paddleOCR
ENV PYTHONBUFFERED=0
RUN pip install paddlepaddle==2.5.2
RUN pip install "paddleocr>=2.0.1" 
RUN pip install gradio
RUN pip install PyMuPDF
RUN pip install python-magic
RUN pip install pdf2image
RUN pip install pdfplumber
RUN pip install pymupdf
RUN pip install numpy
RUn pip install pillow
RUN pip install torch
RUN apt-get update && apt-get install poppler-utils ffmpeg libsm6 libxext6 -y
COPY . .
CMD ["python", "PDFpaddlewithBoxes.py"]
EXPOSE 8089