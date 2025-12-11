FROM python:3.12.0-slim-bookworm

# Environment variables
ENV PYTHONBUFFERED=1
ENV PYTHONWRITEBYTECODE=1
ENV APP=/app

# Create app directory
WORKDIR $APP

# Install dependencies
COPY requirements.txt $APP
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY . $APP

# Collect static files
RUN python manage.py collectstatic --noinput

# Fix ownership and permissions for non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app \
    && chmod -R 775 /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Entrypoint
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/bin/bash","/app/entrypoint.sh"]

# Default command
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "djangoproj.wsgi"]
