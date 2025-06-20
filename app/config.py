# Description : for saving all the configurations required (PostgreSQL, Swagger)

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://root:root@db:5432/jobdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Swagger
    API_TITLE = "Job Scheduler Microservice"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
