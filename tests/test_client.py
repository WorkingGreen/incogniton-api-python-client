"""Unit tests for the Incogniton Python client.

All HTTP calls are mocked — no running Incogniton instance required.
"""
import base64
import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from incogniton import IncognitonClient
from incogniton.api.client import (
    AutomationOperations,
    CookieOperations,
    DEFAULT_BASE_URL,
    IncognitonAPIError,
    IncognitonError,
    ProfileOperations,
    SystemOperations,
)
from incogniton.models import (
    BrowserProfile,
    CreateBrowserProfileRequest,
    GetCookieResponse,
    Navigator,
    Proxy,
    ProfileStatus,
    Timezone,
    UpdateBrowserProfileRequest,
    WebRTC,
)
from incogniton.utils.http.errors import IncognitonError as HttpIncognitonError

PROFILE_ID = "abc123-test-profile-id"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_http():
    """Return a MagicMock HttpAgent with AsyncMock for every HTTP method."""
    m = MagicMock()
    m.get = AsyncMock()
    m.get_text = AsyncMock()
    m.post = AsyncMock()
    return m


# ─────────────────────────────────────────────────────────────────────────────
# Client initialisation
# ─────────────────────────────────────────────────────────────────────────────

class TestClientInit:
    def test_default_url_contains_35000(self):
        client = IncognitonClient()
        assert "35000" in client.http.base_url

    def test_default_base_url_constant(self):
        assert DEFAULT_BASE_URL == "http://localhost:35000"

    def test_custom_base_url_positional(self):
        client = IncognitonClient("http://localhost:9999")
        assert "9999" in client.http.base_url

    def test_custom_base_url_keyword(self):
        client = IncognitonClient(base_url="http://localhost:9999")
        assert "9999" in client.http.base_url

    def test_port_kwarg_builds_localhost_url(self):
        client = IncognitonClient(port=40000)
        assert client.http.base_url == "http://localhost:40000"

    def test_port_kwarg_overrides_default(self):
        client = IncognitonClient(port=12345)
        assert "12345" in client.http.base_url
        assert "35000" not in client.http.base_url

    def test_port_and_base_url_port_wins(self):
        client = IncognitonClient(base_url="http://localhost:9999", port=11111)
        assert "11111" in client.http.base_url
        assert "9999" not in client.http.base_url

    def test_system_property_type(self):
        assert isinstance(IncognitonClient().system, SystemOperations)

    def test_profile_property_type(self):
        assert isinstance(IncognitonClient().profile, ProfileOperations)

    def test_cookie_property_type(self):
        assert isinstance(IncognitonClient().cookie, CookieOperations)

    def test_automation_property_type(self):
        assert isinstance(IncognitonClient().automation, AutomationOperations)

    def test_properties_share_same_http_instance(self):
        client = IncognitonClient()
        assert client.profile.http is client.cookie.http
        assert client.cookie.http is client.automation.http


# ─────────────────────────────────────────────────────────────────────────────
# SystemOperations
# ─────────────────────────────────────────────────────────────────────────────

class TestSystemOperations:
    async def test_alive_calls_get_text(self):
        http = make_http()
        http.get_text.return_value = "OK"
        result = await SystemOperations(http).alive()
        http.get_text.assert_awaited_once_with("/alive")
        assert result == "OK"

    async def test_alive_strips_quoted_form(self):
        """V4 / current V5 serve the JSON-quoted '\"OK\"' — normalize to OK."""
        http = make_http()
        http.get_text.return_value = '"OK"'
        result = await SystemOperations(http).alive()
        assert result == "OK"

    async def test_alive_strips_surrounding_whitespace(self):
        http = make_http()
        http.get_text.return_value = '"OK"\n'
        result = await SystemOperations(http).alive()
        assert result == "OK"

    async def test_alive_bare_form_unchanged(self):
        http = make_http()
        http.get_text.return_value = "OK"
        result = await SystemOperations(http).alive()
        assert result == "OK"

    async def test_close_calls_correct_endpoint(self):
        http = make_http()
        http.get.return_value = {"status": "ok", "message": "Closing"}
        result = await SystemOperations(http).close()
        http.get.assert_awaited_once_with("/incogniton/close")
        assert result["message"] == "Closing"


# ─────────────────────────────────────────────────────────────────────────────
# ProfileOperations
# ─────────────────────────────────────────────────────────────────────────────

class TestProfileList:
    async def test_list_calls_correct_endpoint(self):
        http = make_http()
        http.get.return_value = {"profileData": [], "status": "ok"}
        result = await ProfileOperations(http).list()
        http.get.assert_awaited_once_with("/profile/all")
        assert result["status"] == "ok"


class TestProfileGet:
    async def test_get_calls_correct_endpoint(self):
        http = make_http()
        http.get.return_value = {"profileData": {}, "status": "ok"}
        await ProfileOperations(http).get(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/get/{PROFILE_ID}")


class TestProfileAdd:
    async def test_add_with_request_object(self):
        http = make_http()
        http.post.return_value = {"profile_browser_id": PROFILE_ID, "status": "ok"}
        req = CreateBrowserProfileRequest(profileData={"general_profile_information": {"profile_name": "Test"}})
        result = await ProfileOperations(http).add(req)
        assert http.post.called
        args, kwargs = http.post.call_args
        assert args[0] == "/profile/add"
        assert kwargs["headers"]["Content-Type"] == "application/x-www-form-urlencoded"
        assert "profileData" in kwargs["data"]
        parsed = json.loads(kwargs["data"]["profileData"])
        assert parsed["general_profile_information"]["profile_name"] == "Test"
        assert result["status"] == "ok"

    async def test_add_with_dict_input(self):
        http = make_http()
        http.post.return_value = {"profile_browser_id": PROFILE_ID, "status": "ok"}
        data = {"profileData": {"general_profile_information": {"profile_name": "Dict Test"}}}
        await ProfileOperations(http).add(data)
        args, kwargs = http.post.call_args
        assert args[0] == "/profile/add"

    async def test_add_invalid_type_raises_api_error(self):
        http = make_http()
        with pytest.raises(IncognitonAPIError):
            await ProfileOperations(http).add(12345)

    async def test_add_invalid_object_type_raises_api_error(self):
        http = make_http()
        with pytest.raises(IncognitonAPIError):
            await ProfileOperations(http).add(object())


class TestProfileUpdate:
    async def test_update_sends_to_correct_endpoint(self):
        http = make_http()
        http.post.return_value = {"message": "Profile updated", "status": "ok"}
        req = UpdateBrowserProfileRequest(profileData={"general_profile_information": {"profile_name": "Updated"}})
        await ProfileOperations(http).update(PROFILE_ID, req)
        args, kwargs = http.post.call_args
        assert args[0] == "/profile/update"
        assert kwargs["headers"]["Content-Type"] == "application/x-www-form-urlencoded"

    async def test_update_embeds_profile_id_in_payload(self):
        http = make_http()
        http.post.return_value = {"message": "Profile updated", "status": "ok"}
        req = UpdateBrowserProfileRequest(profileData={"some_field": "value"})
        await ProfileOperations(http).update(PROFILE_ID, req)
        _, kwargs = http.post.call_args
        parsed = json.loads(kwargs["data"]["profileData"])
        assert parsed["profile_browser_id"] == PROFILE_ID

    async def test_update_with_dict_input(self):
        http = make_http()
        http.post.return_value = {"message": "Profile updated", "status": "ok"}
        await ProfileOperations(http).update(PROFILE_ID, {"profileData": {"key": "val"}})
        assert http.post.called

    async def test_update_invalid_type_raises_api_error(self):
        http = make_http()
        with pytest.raises(IncognitonAPIError):
            await ProfileOperations(http).update(PROFILE_ID, "bad input")


class TestProfileSwitchProxy:
    async def test_switch_proxy_delegates_to_update(self):
        http = make_http()
        http.post.return_value = {"message": "Profile updated", "status": "ok"}
        proxy = Proxy(connection_type="HTTP", proxy_url="http://proxy.example.com:8080")
        await ProfileOperations(http).switch_proxy(PROFILE_ID, proxy)
        assert http.post.called
        args, _ = http.post.call_args
        assert args[0] == "/profile/update"

    async def test_switch_proxy_serializes_model_to_json(self):
        """A Proxy model must be serialized to a plain dict (JSON-serializable)."""
        http = make_http()
        http.post.return_value = {"message": "Profile updated", "status": "ok"}
        proxy = Proxy(connection_type="HTTP", proxy_url="http://proxy.example.com:8080")
        await ProfileOperations(http).switch_proxy(PROFILE_ID, proxy)
        _, kwargs = http.post.call_args
        parsed = json.loads(kwargs["data"]["profileData"])
        assert parsed["Proxy"]["connection_type"] == "HTTP"
        assert parsed["Proxy"]["proxy_url"] == "http://proxy.example.com:8080"
        assert parsed["profile_browser_id"] == PROFILE_ID

    async def test_switch_proxy_accepts_plain_dict(self):
        http = make_http()
        http.post.return_value = {"message": "Profile updated", "status": "ok"}
        proxy = {"connection_type": "SOCKS5", "proxy_url": "socks5://1.2.3.4:1080"}
        await ProfileOperations(http).switch_proxy(PROFILE_ID, proxy)
        _, kwargs = http.post.call_args
        parsed = json.loads(kwargs["data"]["profileData"])
        assert parsed["Proxy"]["connection_type"] == "SOCKS5"


class TestProfileLaunch:
    async def test_launch(self):
        http = make_http()
        http.get.return_value = {"message": "Profile launched", "status": "ok"}
        await ProfileOperations(http).launch(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/launch/{PROFILE_ID}")

    async def test_launch_force_local(self):
        http = make_http()
        http.get.return_value = {"message": "Profile launched", "status": "ok"}
        await ProfileOperations(http).launch_force_local(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/launch/{PROFILE_ID}/force/local")

    async def test_launch_force_cloud(self):
        http = make_http()
        http.get.return_value = {"message": "Profile launched", "status": "ok"}
        await ProfileOperations(http).launch_force_cloud(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/launch/{PROFILE_ID}/force/cloud")


class TestProfileDryLaunch:
    async def test_dry_launch(self):
        http = make_http()
        http.get.return_value = {"arg": "--some --args", "status": "ok"}
        result = await ProfileOperations(http).dry_launch(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/dryLaunch/{PROFILE_ID}")
        assert result["arg"] == "--some --args"

    async def test_dry_launch_force_local(self):
        http = make_http()
        http.get.return_value = {"arg": "--some --args", "status": "ok"}
        await ProfileOperations(http).dry_launch_force_local(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/dryLaunch/{PROFILE_ID}/force/local")

    async def test_dry_launch_force_cloud(self):
        http = make_http()
        http.get.return_value = {"arg": "--some --args", "status": "ok"}
        await ProfileOperations(http).dry_launch_force_cloud(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/dryLaunch/{PROFILE_ID}/force/cloud")


class TestProfileStatus:
    async def test_get_status(self):
        http = make_http()
        http.get.return_value = {"status": "Ready"}
        result = await ProfileOperations(http).get_status(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/status/{PROFILE_ID}")
        assert result["status"] == "Ready"

    async def test_stop(self):
        http = make_http()
        http.get.return_value = {"message": "Profile stopped", "status": "ok"}
        await ProfileOperations(http).stop(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/stop/{PROFILE_ID}")

    async def test_force_stop(self):
        http = make_http()
        http.get.return_value = {"message": "Profile force stopped", "status": "ok"}
        await ProfileOperations(http).force_stop(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/force-stop/{PROFILE_ID}")


class TestProfileDelete:
    async def test_delete(self):
        http = make_http()
        http.get.return_value = {"message": "Profile removed", "status": "ok"}
        await ProfileOperations(http).delete(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/delete/{PROFILE_ID}")


class TestProfileClone:
    async def test_clone_minimal_sends_only_id(self):
        http = make_http()
        http.post.return_value = {"profile_browser_id": "new-id", "status": "ok"}
        result = await ProfileOperations(http).clone(PROFILE_ID)
        http.post.assert_awaited_once_with(
            "/profile/clone", data={"profile_browser_id": PROFILE_ID}
        )
        assert result["profile_browser_id"] == "new-id"

    async def test_clone_with_all_options(self):
        http = make_http()
        http.post.return_value = {"profile_browser_id": "new-id", "status": "ok"}
        await ProfileOperations(http).clone(
            PROFILE_ID,
            profile_name="My Clone",
            target_group="Work",
            clone_cookies=False,
            clone_advanced_other_settings=True,
            clone_useragent=False,
            clone_other_browser_data=True,
        )
        _, kwargs = http.post.call_args
        data = kwargs["data"]
        assert data["profile_browser_id"] == PROFILE_ID
        assert data["profile_name"] == "My Clone"
        assert data["target_group"] == "Work"
        assert data["clone_cookies"] is False
        assert data["clone_advanced_other_settings"] is True
        assert data["clone_useragent"] is False
        assert data["clone_other_browser_data"] is True

    async def test_clone_omits_none_options(self):
        http = make_http()
        http.post.return_value = {"profile_browser_id": "new-id", "status": "ok"}
        await ProfileOperations(http).clone(PROFILE_ID, profile_name="Named")
        _, kwargs = http.post.call_args
        data = kwargs["data"]
        assert "clone_cookies" not in data
        assert "clone_useragent" not in data
        assert data["profile_name"] == "Named"

    async def test_clone_quick(self):
        http = make_http()
        http.get.return_value = {"profile_browser_id": "new-id", "status": "ok"}
        result = await ProfileOperations(http).clone_quick(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/clone/{PROFILE_ID}")
        assert result["profile_browser_id"] == "new-id"


# ─────────────────────────────────────────────────────────────────────────────
# CookieOperations
# ─────────────────────────────────────────────────────────────────────────────

class TestCookieOperations:
    async def test_get(self):
        http = make_http()
        http.get.return_value = {"CookieData ": [], "message": "Successfully exported cookies", "status": "ok"}
        result = await CookieOperations(http).get(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/cookie/{PROFILE_ID}")
        assert result["status"] == "ok"

    async def test_add_encodes_cookies_as_base64json(self):
        http = make_http()
        http.post.return_value = {"message": "Cookies imported", "status": "ok"}
        cookie_data = [{"name": "session", "value": "xyz", "domain": ".example.com", "path": "/", "secure": True}]
        await CookieOperations(http).add(PROFILE_ID, cookie_data)

        args, kwargs = http.post.call_args
        assert args[0] == "/profile/addCookie"
        sent = kwargs["data"]
        assert sent["profile_browser_id"] == PROFILE_ID
        assert sent["format"] == "base64json"
        decoded = json.loads(base64.b64decode(sent["cookie"]))
        assert decoded[0]["name"] == "session"
        assert decoded[0]["value"] == "xyz"

    async def test_add_multiple_cookies(self):
        http = make_http()
        http.post.return_value = {"message": "Cookies imported", "status": "ok"}
        cookies = [
            {"name": "a", "value": "1"},
            {"name": "b", "value": "2"},
        ]
        await CookieOperations(http).add(PROFILE_ID, cookies)
        _, kwargs = http.post.call_args
        decoded = json.loads(base64.b64decode(kwargs["data"]["cookie"]))
        assert len(decoded) == 2
        assert decoded[1]["name"] == "b"

    async def test_delete(self):
        http = make_http()
        http.get.return_value = {"message": "Cookies successfully deleted", "status": "ok"}
        result = await CookieOperations(http).delete(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/profile/deleteCookie/{PROFILE_ID}")
        assert result["status"] == "ok"


# ─────────────────────────────────────────────────────────────────────────────
# AutomationOperations
# ─────────────────────────────────────────────────────────────────────────────

class TestPuppeteerAutomation:
    async def test_launch_puppeteer(self):
        http = make_http()
        http.get.return_value = {"puppeteerUrl": "http://127.0.0.1:60128", "status": "ok"}
        result = await AutomationOperations(http).launch_puppeteer(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/automation/launch/puppeteer/{PROFILE_ID}")
        assert result["puppeteerUrl"] == "http://127.0.0.1:60128"

    async def test_launch_puppeteer_force_local(self):
        http = make_http()
        http.get.return_value = {"puppeteerUrl": "http://127.0.0.1:60128", "status": "ok"}
        await AutomationOperations(http).launch_puppeteer_force_local(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/automation/launch/puppeteer/{PROFILE_ID}/local")

    async def test_launch_puppeteer_force_cloud(self):
        http = make_http()
        http.get.return_value = {"puppeteerUrl": "http://127.0.0.1:60128", "status": "ok"}
        await AutomationOperations(http).launch_puppeteer_force_cloud(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/automation/launch/puppeteer/{PROFILE_ID}/cloud")

    async def test_launch_puppeteer_custom(self):
        http = make_http()
        http.post.return_value = {"puppeteerUrl": "http://127.0.0.1:60128", "status": "ok"}
        await AutomationOperations(http).launch_puppeteer_custom(PROFILE_ID, "--headless=new")
        http.post.assert_awaited_once_with(
            "/automation/launch/puppeteer",
            data={"profileID": PROFILE_ID, "customArgs": "--headless=new"},
        )


class TestSeleniumAutomation:
    async def test_launch_selenium(self):
        http = make_http()
        http.get.return_value = {"url": "127.0.0.1:9515/abc", "status": "ok"}
        result = await AutomationOperations(http).launch_selenium(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/automation/launch/python/{PROFILE_ID}")
        assert "url" in result

    async def test_launch_selenium_force_local(self):
        http = make_http()
        http.get.return_value = {"url": "127.0.0.1:9515/abc", "status": "ok"}
        await AutomationOperations(http).launch_selenium_force_local(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/automation/launch/python/{PROFILE_ID}/local")

    async def test_launch_selenium_force_cloud(self):
        http = make_http()
        http.get.return_value = {"url": "127.0.0.1:9515/abc", "status": "ok"}
        await AutomationOperations(http).launch_selenium_force_cloud(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/automation/launch/python/{PROFILE_ID}/cloud")

    async def test_launch_selenium_custom_path(self):
        http = make_http()
        http.post.return_value = {"url": "127.0.0.1:9515/abc", "status": "ok"}
        await AutomationOperations(http).launch_selenium_custom(PROFILE_ID, "--headless=new")
        http.post.assert_awaited_once_with(
            f"/automation/launch/python/{PROFILE_ID}/",
            data={"customArgs": "--headless=new"},
        )

    async def test_launch_selenium_custom_body_minimal(self):
        http = make_http()
        http.post.return_value = {"url": "127.0.0.1:9515/abc", "status": "ok"}
        await AutomationOperations(http).launch_selenium_custom_body(PROFILE_ID)
        http.post.assert_awaited_once_with(
            "/automation/launch/python/",
            data={"profileID": PROFILE_ID},
        )

    async def test_launch_selenium_custom_body_with_custom_args(self):
        http = make_http()
        http.post.return_value = {"url": "127.0.0.1:9515/abc", "status": "ok"}
        await AutomationOperations(http).launch_selenium_custom_body(
            PROFILE_ID, custom_args="--headless=new"
        )
        _, kwargs = http.post.call_args
        assert kwargs["data"]["customArgs"] == "--headless=new"
        assert "forceLocal" not in kwargs["data"]
        assert "forceCloud" not in kwargs["data"]

    async def test_launch_selenium_custom_body_force_local(self):
        http = make_http()
        http.post.return_value = {"url": "127.0.0.1:9515/abc", "status": "ok"}
        await AutomationOperations(http).launch_selenium_custom_body(
            PROFILE_ID, force_local=True
        )
        _, kwargs = http.post.call_args
        assert kwargs["data"]["forceLocal"] is True
        assert "forceCloud" not in kwargs["data"]

    async def test_launch_selenium_custom_body_force_cloud(self):
        http = make_http()
        http.post.return_value = {"url": "127.0.0.1:9515/abc", "status": "ok"}
        await AutomationOperations(http).launch_selenium_custom_body(
            PROFILE_ID, force_cloud=True
        )
        _, kwargs = http.post.call_args
        assert kwargs["data"]["forceCloud"] is True
        assert "forceLocal" not in kwargs["data"]

    async def test_launch_selenium_custom_body_all_options(self):
        http = make_http()
        http.post.return_value = {"url": "127.0.0.1:9515/abc", "status": "ok"}
        await AutomationOperations(http).launch_selenium_custom_body(
            PROFILE_ID, custom_args="--headless=new", force_local=True, force_cloud=False
        )
        _, kwargs = http.post.call_args
        d = kwargs["data"]
        assert d["profileID"] == PROFILE_ID
        assert d["customArgs"] == "--headless=new"
        assert d["forceLocal"] is True
        assert "forceCloud" not in d


class TestCookieRobot:
    async def test_launch_cookie_robot(self):
        http = make_http()
        http.get.return_value = {"message": "Cookie robot launched", "status": "ok"}
        result = await AutomationOperations(http).launch_cookie_robot(PROFILE_ID)
        http.get.assert_awaited_once_with(f"/automation/cookieRobot/{PROFILE_ID}")
        assert result["message"] == "Cookie robot launched"


# ─────────────────────────────────────────────────────────────────────────────
# Error handling
# ─────────────────────────────────────────────────────────────────────────────

class TestErrorHandling:
    async def test_http_error_propagates_from_list(self):
        http = make_http()
        http.get.side_effect = HttpIncognitonError("Connection refused")
        with pytest.raises(HttpIncognitonError):
            await ProfileOperations(http).list()

    async def test_http_error_propagates_from_launch(self):
        http = make_http()
        http.get.side_effect = HttpIncognitonError("Timeout")
        with pytest.raises(HttpIncognitonError):
            await ProfileOperations(http).launch(PROFILE_ID)

    async def test_http_error_propagates_from_cookie_get(self):
        http = make_http()
        http.get.side_effect = HttpIncognitonError("Not found")
        with pytest.raises(HttpIncognitonError):
            await CookieOperations(http).get(PROFILE_ID)

    async def test_http_error_propagates_from_automation(self):
        http = make_http()
        http.get.side_effect = HttpIncognitonError("Service unavailable")
        with pytest.raises(HttpIncognitonError):
            await AutomationOperations(http).launch_puppeteer(PROFILE_ID)

    async def test_add_profile_wraps_error_as_api_error(self):
        http = make_http()
        with pytest.raises(IncognitonAPIError):
            await ProfileOperations(http).add("not-a-valid-type")

    async def test_update_profile_wraps_error_as_api_error(self):
        http = make_http()
        with pytest.raises(IncognitonAPIError):
            await ProfileOperations(http).update(PROFILE_ID, 999)

    async def test_incogniton_error_is_catchable_as_base_exception(self):
        http = make_http()
        http.get.side_effect = HttpIncognitonError("fail")
        with pytest.raises(Exception):
            await ProfileOperations(http).list()


# ─────────────────────────────────────────────────────────────────────────────
# Backwards compatibility
# ─────────────────────────────────────────────────────────────────────────────

class TestBackwardsCompatibility:
    def test_incogniton_error_importable_from_client(self):
        from incogniton.api.client import IncognitonError as E
        assert E is not None

    def test_incogniton_api_error_importable_from_client(self):
        from incogniton.api.client import IncognitonAPIError as E
        assert E is not None

    def test_error_classes_are_same_as_http_module(self):
        from incogniton.api.client import IncognitonError as ClientError
        from incogniton.utils.http.errors import IncognitonError as HttpError
        assert ClientError is HttpError

    def test_api_error_is_subclass_of_incogniton_error(self):
        assert issubclass(IncognitonAPIError, IncognitonError)

    def test_client_importable_from_top_level(self):
        from incogniton import IncognitonClient as C
        assert C is not None

    def test_browser_importable_from_top_level(self):
        from incogniton import IncognitonBrowser as B
        assert B is not None

    def test_create_profile_request_importable(self):
        from incogniton.models import CreateBrowserProfileRequest
        assert CreateBrowserProfileRequest is not None

    def test_update_profile_request_importable(self):
        from incogniton.models import UpdateBrowserProfileRequest
        assert UpdateBrowserProfileRequest is not None

    def test_browser_profile_importable(self):
        from incogniton.models import BrowserProfile
        assert BrowserProfile is not None

    def test_proxy_importable(self):
        from incogniton.models import Proxy
        assert Proxy is not None

    def test_get_cookie_response_importable(self):
        from incogniton.models import GetCookieResponse
        assert GetCookieResponse is not None

    def test_positional_base_url_still_accepted(self):
        client = IncognitonClient("http://localhost:9999")
        assert "9999" in client.http.base_url

    def test_no_args_constructor_still_works(self):
        client = IncognitonClient()
        assert client is not None

    def test_default_port_is_35000(self):
        client = IncognitonClient()
        assert "35000" in client.http.base_url
