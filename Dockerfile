FROM python:3.9-slim

WORKDIR /app

# 复制requirements.txt
COPY requirements-web.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements-web.txt && \
    pip install --no-cache-dir PyMuPDF==1.22.3 python-docx==0.8.11

# 复制应用程序代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=src/web/app.py
ENV FLASK_ENV=production
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

# 创建数据目录
RUN mkdir -p /app/data/uploads/templates
RUN mkdir -p /app/data/uploads/annotations
RUN mkdir -p /app/data/uploads/outputs
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.web.app:app"] 