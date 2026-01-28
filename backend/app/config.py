
class BaseConfig:
	# Env-based settings are applied in create_app() after load_dotenv().
	SECRET_KEY = "dev"


class DevelopmentConfig(BaseConfig):
	DEBUG = True


class TestingConfig(BaseConfig):
	TESTING = True


class ProductionConfig(BaseConfig):
	DEBUG = False


CONFIG_BY_NAME: dict[str, type[BaseConfig]] = {
	"development": DevelopmentConfig,
	"testing": TestingConfig,
	"production": ProductionConfig,
}


