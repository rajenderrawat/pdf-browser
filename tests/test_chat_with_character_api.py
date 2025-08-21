import json
from types import SimpleNamespace

import pytest


class DummyUser:
	@property
	def is_authenticated(self):
		return True


class _SaveCollector:
	def __init__(self):
		self.saved_instances = []

	def make_model_class(self, name):
		collector = self

		class _Model:
			def __init__(self, **kwargs):
				self._data = kwargs

			def save(self):
				collector.saved_instances.append(self)

			def __repr__(self):
				return f"<{name} {self._data}>"

		return _Model


def _build_request(api_view_cls, data, rf, user=None):
	view = api_view_cls.as_view()
	req = rf.post("/api/chat/", data=json.dumps(data), content_type="application/json")
	# Force auth by attaching a user directly
	req.user = user or DummyUser()
	return view, req


@pytest.fixture
def rf():
	from django.test import RequestFactory
	return RequestFactory()


def _import_or_skip_view_module():
	# Try multiple likely module paths to locate ChatWithCharacterAPIView
	possible_modules = [
		"ChatGeneration_Service.views",
		"ChatGeneration_Service.api.views",
		"ChatGeneration_Service.views.chat",
	]
	last_err = None
	for name in possible_modules:
		try:
			mod = pytest.importorskip(name)
			if hasattr(mod, "ChatWithCharacterAPIView"):
				return mod
		except Exception as exc:  # pragma: no cover - import resolution helper
			last_err = exc
	pytest.skip(f"Could not import ChatWithCharacterAPIView from any known module: {last_err}")


def test_chat_with_character_success_returns_200_and_saves_messages(rf, monkeypatch):
	mod = _import_or_skip_view_module()

	# Prepare collectors and dummy models
	chat_msg_collector = _SaveCollector()
	prompt_collector = _SaveCollector()
	DummyChatMessage = chat_msg_collector.make_model_class("ChatMessage")
	DummyChatPromptResponse = prompt_collector.make_model_class("ChatPromptResponse")

	# Monkeypatch model classes used by the view
	monkeypatch.setattr(mod, "ChatMessage", DummyChatMessage, raising=True)
	monkeypatch.setattr(mod, "ChatPromptResponse", DummyChatPromptResponse, raising=True)

	# Monkeypatch Character.objects.get to return a dummy
	class _Mgr:
		@staticmethod
		def get(**kwargs):
			return SimpleNamespace(id=kwargs.get("_id"))

	class _DummyCharacter:
		objects = _Mgr()

	monkeypatch.setattr(mod, "Character", _DummyCharacter, raising=True)

	# Monkeypatch chat_with_character to return predictable output
	def fake_chat_with_character(character, character_id, session_id, user_message):
		return "Hello from AI", [{"role": "user", "content": user_message}]

	monkeypatch.setattr(mod, "chat_with_character", fake_chat_with_character, raising=True)

	# Build and execute request
	data = {
		"character_id": "507f1f77bcf86cd799439011",  # valid 24-hex string shape
		"session_id": "session-123",
		"creator_id": "creator-abc",
		"message": "Hi there!",
	}
	# Disable permission checks for unit test logic focus
	mod.ChatWithCharacterAPIView.permission_classes = []
	view, req = _build_request(mod.ChatWithCharacterAPIView, data, rf)
	resp = view(req)

	assert resp.status_code == 200
	body = json.loads(resp.content)
	assert body["reply"] == "Hello from AI"

	# Validate that two ChatMessage entries were saved (user and ai)
	assert len(chat_msg_collector.saved_instances) == 2
	user_msg = chat_msg_collector.saved_instances[0]
	ai_msg = chat_msg_collector.saved_instances[1]
	assert user_msg._data["sender"] == "user"
	assert ai_msg._data["sender"] == "ai"

	# Validate prompt-response saved with expected fields
	assert len(prompt_collector.saved_instances) == 1
	pr = prompt_collector.saved_instances[0]
	assert pr._data["creator_id"] == data["creator_id"]
	assert pr._data["character_id"] == data["character_id"]
	assert pr._data["user_input"] == data["message"]
	assert pr._data["response"] == "Hello from AI"


def test_chat_with_character_character_not_found_returns_404(rf, monkeypatch):
	mod = _import_or_skip_view_module()

	# Provide dummy model classes (not strictly needed for 404 path)
	chat_msg_collector = _SaveCollector()
	DummyChatMessage = chat_msg_collector.make_model_class("ChatMessage")
	monkeypatch.setattr(mod, "ChatMessage", DummyChatMessage, raising=True)

	# Configure Character.objects.get to raise DoesNotExist
	class _DoesNotExist(Exception):
		pass

	class _Mgr:
		@staticmethod
		def get(**kwargs):
			raise _DoesNotExist()

	class _DummyCharacter:
		DoesNotExist = _DoesNotExist
		objects = _Mgr()

	monkeypatch.setattr(mod, "Character", _DummyCharacter, raising=True)

	# Mock chat function just in case, though it should not be called
	monkeypatch.setattr(mod, "chat_with_character", lambda *a, **k: ("AI", []), raising=True)

	data = {
		"character_id": "507f1f77bcf86cd799439011",
		"session_id": "session-404",
		"creator_id": "creator-xyz",
		"message": "Hello?",
	}
	mod.ChatWithCharacterAPIView.permission_classes = []
	view, req = _build_request(mod.ChatWithCharacterAPIView, data, rf)
	resp = view(req)

	assert resp.status_code == 404
	body = json.loads(resp.content)
	assert body["error"] == "Character not found"


def test_chat_with_character_internal_error_returns_500(rf, monkeypatch):
	mod = _import_or_skip_view_module()

	# Dummy models
	chat_msg_collector = _SaveCollector()
	DummyChatMessage = chat_msg_collector.make_model_class("ChatMessage")
	DummyChatPromptResponse = _SaveCollector().make_model_class("ChatPromptResponse")
	monkeypatch.setattr(mod, "ChatMessage", DummyChatMessage, raising=True)
	monkeypatch.setattr(mod, "ChatPromptResponse", DummyChatPromptResponse, raising=True)

	# Character exists
	class _Mgr:
		@staticmethod
		def get(**kwargs):
			return SimpleNamespace(id=kwargs.get("_id"))

	class _DummyCharacter:
		objects = _Mgr()

	monkeypatch.setattr(mod, "Character", _DummyCharacter, raising=True)

	# Force an exception inside the handler (e.g., chat layer fails)
	def boom(*args, **kwargs):
		raise RuntimeError("OpenAI down")

	monkeypatch.setattr(mod, "chat_with_character", boom, raising=True)

	data = {
		"character_id": "507f1f77bcf86cd799439011",
		"session_id": "session-500",
		"creator_id": "creator-err",
		"message": "Ping",
	}
	mod.ChatWithCharacterAPIView.permission_classes = []
	view, req = _build_request(mod.ChatWithCharacterAPIView, data, rf)
	resp = view(req)

	assert resp.status_code == 500
	body = json.loads(resp.content)
	assert body["message"] == "Error occurred"
	assert "OpenAI down" in body["error"]

