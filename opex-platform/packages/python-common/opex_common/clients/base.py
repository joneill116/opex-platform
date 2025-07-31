import httpx
from typing import Optional, Dict, Any, TypeVar, Type
from tenacity import retry, stop_after_attempt, wait_exponential
from opentelemetry import trace
from opentelemetry.propagate import inject
import structlog
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)
logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)

class ServiceException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Service error {status_code}: {detail}")

class BaseServiceClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=timeout)
        self.logger = logger.bind(service=self.__class__.__name__)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    async def close(self):
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def _request(
        self,
        method: str,
        path: str,
        response_model: Optional[Type[T]] = None,
        **kwargs
    ) -> Dict[str, Any] | T:
        with tracer.start_as_current_span(f"{self.__class__.__name__}.{method} {path}") as span:
            headers = kwargs.pop("headers", {})
            inject(headers)
            
            span.set_attribute("http.method", method)
            span.set_attribute("http.url", f"{self.base_url}{path}")
            span.set_attribute("service.name", self.__class__.__name__)
            
            try:
                response = await self.client.request(
                    method=method,
                    url=f"{self.base_url}{path}",
                    headers=headers,
                    **kwargs
                )
                
                span.set_attribute("http.status_code", response.status_code)
                
                if response.status_code >= 400:
                    error_detail = response.json().get("detail", "Unknown error")
                    span.set_status(trace.Status(trace.StatusCode.ERROR, error_detail))
                    raise ServiceException(response.status_code, error_detail)
                
                data = response.json()
                
                if response_model:
                    return response_model(**data)
                
                return data
                
            except httpx.RequestError as e:
                self.logger.error("request_failed", error=str(e), method=method, path=path)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
            except Exception as e:
                self.logger.error("unexpected_error", error=str(e), method=method, path=path)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
    
    async def get(self, path: str, **kwargs):
        return await self._request("GET", path, **kwargs)
    
    async def post(self, path: str, **kwargs):
        return await self._request("POST", path, **kwargs)
    
    async def put(self, path: str, **kwargs):
        return await self._request("PUT", path, **kwargs)
    
    async def patch(self, path: str, **kwargs):
        return await self._request("PATCH", path, **kwargs)
    
    async def delete(self, path: str, **kwargs):
        return await self._request("DELETE", path, **kwargs)
