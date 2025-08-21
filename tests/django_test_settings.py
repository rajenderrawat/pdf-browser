SECRET_KEY = "test-secret-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
	"django.contrib.contenttypes",
	"django.contrib.auth",
	"rest_framework",
	# Your app module that contains ChatGeneration_Service.views should be importable.
	# If the project uses an app config, add it here. Keeping minimal for unit-level tests.
]

MIDDLEWARE = []

ROOT_URLCONF = "tests.test_urls"

DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.sqlite3",
		"NAME": ":memory:",
	}
}

USE_TZ = True
TIME_ZONE = "UTC"

REST_FRAMEWORK = {
	"DEFAULT_AUTHENTICATION_CLASSES": [],
	"DEFAULT_PERMISSION_CLASSES": [],
}

