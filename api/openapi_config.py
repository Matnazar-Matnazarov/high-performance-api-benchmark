"""
OpenAPI configuration with JWT Bearer security for Swagger UI.

Defines BearerAuth (JWT) in components.securitySchemes so Swagger UI
shows the "Authorize" button and lets users paste the token from POST /auth/login.
"""

from django.conf import settings
from django_bolt.openapi import OpenAPIConfig
from django_bolt.openapi.plugins import (
    RapidocRenderPlugin,
    RedocRenderPlugin,
    ScalarRenderPlugin,
    StoplightRenderPlugin,
    SwaggerRenderPlugin,
)
from django_bolt.openapi.spec import Components, SecurityScheme


def get_openapi_config() -> OpenAPIConfig:
    """Build OpenAPI config with JWT Bearer security scheme for Swagger/Redoc/Scalar."""
    title = (
        getattr(settings, "PROJECT_NAME", "Django - Bolt API")
        or getattr(settings, "SITE_NAME", "Django - Bolt API")
        or "API"
    )
    return OpenAPIConfig(
        title=title,
        version="1.0.0",
        path="/docs",
        components=Components(
            security_schemes={
                "BearerAuth": SecurityScheme(
                    type="http",
                    scheme="bearer",
                    bearer_format="JWT",
                    description=(
                        "JWT access token. Use **POST /auth/login** with `username` and `password` "
                        "to obtain a token, then click **Authorize** and enter: `Bearer <your_token>`."
                    ),
                ),
            },
        ),
        render_plugins=[
            SwaggerRenderPlugin(path="/"),
            RedocRenderPlugin(path="/redoc"),
            ScalarRenderPlugin(path="/scalar"),
            RapidocRenderPlugin(path="/rapidoc"),
            StoplightRenderPlugin(path="/stoplight"),
        ],
        exclude_paths=["/admin", "/static"],
        use_handler_docstrings=True,
        include_error_responses=True,
    )
