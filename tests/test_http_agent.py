"""Unit tests for the HttpAgent transport layer.

Uses httpx.MockTransport so no running Incogniton instance is required.
"""
import httpx
import pytest

from incogniton.utils.http.agent import HttpAgent
from incogniton.utils.http.errors import IncognitonError

BASE_URL = "http://localhost:35000"


def agent_with_handler(handler):
    """Build an HttpAgent whose underlying client uses a MockTransport."""
    agent = HttpAgent(BASE_URL)
    agent._client = httpx.AsyncClient(
        base_url=BASE_URL,
        headers=agent.headers,
        transport=httpx.MockTransport(handler),
    )
    return agent


class TestGetJson:
    async def test_get_returns_parsed_json(self):
        def handler(request):
            assert request.url.path == "/profile/all"
            return httpx.Response(200, json={"status": "ok", "profileData": []})

        agent = agent_with_handler(handler)
        result = await agent.get("/profile/all")
        assert result["status"] == "ok"
        await agent.close()

    async def test_get_raises_on_http_error(self):
        def handler(request):
            return httpx.Response(500, json={"message": "boom"})

        agent = agent_with_handler(handler)
        with pytest.raises(IncognitonError) as exc:
            await agent.get("/profile/all")
        assert exc.value.status_code == 500
        await agent.close()

    async def test_get_error_falls_back_to_text_on_non_json(self):
        def handler(request):
            return httpx.Response(503, text="Service Unavailable")

        agent = agent_with_handler(handler)
        with pytest.raises(IncognitonError) as exc:
            await agent.get("/x")
        assert "Service Unavailable" in str(exc.value)
        await agent.close()


class TestGetText:
    async def test_get_text_returns_raw_body(self):
        def handler(request):
            assert request.url.path == "/alive"
            return httpx.Response(200, text="OK")

        agent = agent_with_handler(handler)
        result = await agent.get_text("/alive")
        assert result == "OK"
        assert isinstance(result, str)
        await agent.close()

    async def test_get_text_raises_on_http_error(self):
        def handler(request):
            return httpx.Response(404, text="not found")

        agent = agent_with_handler(handler)
        with pytest.raises(IncognitonError) as exc:
            await agent.get_text("/alive")
        assert exc.value.status_code == 404
        await agent.close()


class TestPostJson:
    async def test_post_sends_json_body(self):
        captured = {}

        def handler(request):
            captured["body"] = request.content
            captured["content_type"] = request.headers.get("content-type")
            return httpx.Response(200, json={"status": "ok"})

        agent = agent_with_handler(handler)
        result = await agent.post("/profile/clone", data={"profile_browser_id": "abc"})
        assert result["status"] == "ok"
        assert b"profile_browser_id" in captured["body"]
        assert "application/json" in captured["content_type"]
        await agent.close()

    async def test_post_form_urlencoded(self):
        captured = {}

        def handler(request):
            captured["body"] = request.content.decode()
            captured["content_type"] = request.headers.get("content-type")
            return httpx.Response(200, json={"status": "ok"})

        agent = agent_with_handler(handler)
        await agent.post(
            "/profile/add",
            data={"profileData": "{}"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert "application/x-www-form-urlencoded" in captured["content_type"]
        assert "profileData" in captured["body"]
        await agent.close()


class TestConnectionErrors:
    async def test_connect_error_wrapped(self):
        def handler(request):
            raise httpx.ConnectError("refused")

        agent = agent_with_handler(handler)
        with pytest.raises(IncognitonError) as exc:
            await agent.get("/profile/all")
        assert "Connection error" in str(exc.value)
        await agent.close()

    async def test_timeout_wrapped(self):
        def handler(request):
            raise httpx.TimeoutException("slow")

        agent = agent_with_handler(handler)
        with pytest.raises(IncognitonError) as exc:
            await agent.get("/profile/all")
        assert "timed out" in str(exc.value)
        await agent.close()

    async def test_get_text_connect_error_wrapped(self):
        def handler(request):
            raise httpx.ConnectError("refused")

        agent = agent_with_handler(handler)
        with pytest.raises(IncognitonError) as exc:
            await agent.get_text("/alive")
        assert "Connection error" in str(exc.value)
        await agent.close()


class TestPutDelete:
    async def test_put_sends_json_body(self):
        captured = {}

        def handler(request):
            captured["method"] = request.method
            captured["body"] = request.content
            return httpx.Response(200, json={"status": "ok"})

        agent = agent_with_handler(handler)
        result = await agent.put("/some/endpoint", data={"k": "v"})
        assert result["status"] == "ok"
        assert captured["method"] == "PUT"
        assert b"k" in captured["body"]
        await agent.close()

    async def test_delete_calls_endpoint(self):
        captured = {}

        def handler(request):
            captured["method"] = request.method
            captured["path"] = request.url.path
            return httpx.Response(200, json={"status": "ok"})

        agent = agent_with_handler(handler)
        result = await agent.delete("/profile/delete/abc")
        assert result["status"] == "ok"
        assert captured["method"] == "DELETE"
        assert captured["path"] == "/profile/delete/abc"
        await agent.close()


class TestEncodeFormData:
    def test_encode_simple_pair(self):
        agent = HttpAgent(BASE_URL)
        encoded = agent._encode_form_data({"key": "value"})
        assert encoded == "key=value"

    def test_encode_special_characters(self):
        agent = HttpAgent(BASE_URL)
        encoded = agent._encode_form_data({"url": "http://a.com?x=1&y=2"})
        # Special chars must be percent-encoded, no raw & or = leaking through
        assert "key" not in encoded
        assert "%3A" in encoded  # ':' encoded
        assert encoded.startswith("url=")

    def test_encode_multiple_pairs(self):
        agent = HttpAgent(BASE_URL)
        encoded = agent._encode_form_data({"a": "1", "b": "2"})
        assert "a=1" in encoded
        assert "b=2" in encoded
        assert "&" in encoded


class TestAgentConfig:
    def test_default_timeout(self):
        agent = HttpAgent(BASE_URL)
        assert agent.timeout == 35

    def test_custom_timeout(self):
        agent = HttpAgent(BASE_URL, timeout=10)
        assert agent.timeout == 10

    def test_base_url_stored(self):
        agent = HttpAgent("http://localhost:40000")
        assert agent.base_url == "http://localhost:40000"

    def test_default_content_type_header(self):
        agent = HttpAgent(BASE_URL)
        assert agent.headers["Content-Type"] == "application/json"
