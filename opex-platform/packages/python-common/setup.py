from setuptools import setup, find_packages

setup(
    name="opex-common",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.5.0",
        "httpx>=0.26.0",
        "tenacity>=8.2.0",
        "opentelemetry-api>=1.22.0",
        "opentelemetry-sdk>=1.22.0",
        "opentelemetry-instrumentation-fastapi>=0.43b0",
        "opentelemetry-exporter-jaeger>=1.21.0",
        "prometheus-client>=0.19.0",
        "structlog>=24.1.0",
        "python-json-logger>=2.0.7",
    ],
)
