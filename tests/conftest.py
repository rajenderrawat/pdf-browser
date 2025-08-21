import os


# Ensure Django is configured for tests that import DRF/Django components
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.django_test_settings")

try:
	import django  # noqa: F401
	django.setup()
except Exception:
	# If Django isn't available in the environment, tests that need it will be skipped
	pass

