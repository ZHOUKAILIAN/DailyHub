from __future__ import annotations

import json
import sys
import types
import unittest
from unittest.mock import patch

from checkin.xiaojuchongdian.src.config import HttpConfig
from checkin.xiaojuchongdian.src.http import AuthError, HttpClient, HttpClientError, HttpStatusError


class FakeResponse:
    def __init__(
        self,
        status_code: int,
        *,
        payload: dict | None = None,
        text: str = "",
        headers: dict | None = None,
        json_exception: Exception | None = None,
    ) -> None:
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = text
        self.headers = headers or {"x-test": "1"}
        self._json_exception = json_exception

    def json(self) -> dict:
        if self._json_exception is not None:
            raise self._json_exception
        return self._payload


class FakeRequestsModule:
    class RequestException(Exception):
        pass

    def __init__(self, events: list[object]) -> None:
        self._events = list(events)
        self.sessions: list["FakeSession"] = []

    def Session(self) -> "FakeSession":  # noqa: N802
        session = FakeSession(self._events, self.RequestException)
        self.sessions.append(session)
        return session


class FakeSession:
    def __init__(self, events: list[object], request_exc_type: type[Exception]) -> None:
        self._events = list(events)
        self._request_exc_type = request_exc_type
        self.calls: list[dict] = []

    def post(self, url: str, json: dict, headers: dict, timeout: int) -> FakeResponse:
        self.calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        if not self._events:
            raise AssertionError("no fake event left for session.post()")
        event = self._events.pop(0)
        if event == "request_exception":
            raise self._request_exc_type("network down")
        assert isinstance(event, FakeResponse)
        return event


class HttpClientTests(unittest.TestCase):
    def _build_client(
        self, events: list[object], *, retries: int = 1, timeout_seconds: int = 3
    ) -> tuple[HttpClient, FakeSession]:
        fake_requests = FakeRequestsModule(events)
        cfg = HttpConfig(
            timeout_seconds=timeout_seconds,
            retries=retries,
            backoff_seconds=0.01,
            backoff_factor=2.0,
        )
        with patch.dict(sys.modules, {"requests": fake_requests}):
            client = HttpClient(cfg)
        return client, fake_requests.sessions[0]

    def test_post_json_returns_response_on_success(self) -> None:
        client, session = self._build_client(
            [FakeResponse(200, payload={"success": True}, headers={"x-id": "abc"})]
        )
        result = client.post_json("https://example.com", {"a": 1}, {"h": "v"})

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, {"success": True})
        self.assertEqual(result.headers, {"x-id": "abc"})
        self.assertEqual(len(session.calls), 1)

    def test_post_json_raises_auth_error_on_401(self) -> None:
        client, _ = self._build_client([FakeResponse(401, text="unauthorized")], retries=0)
        with self.assertRaises(AuthError):
            client.post_json("https://example.com", {}, {})

    def test_post_json_retries_on_503_then_succeeds(self) -> None:
        client, session = self._build_client(
            [
                FakeResponse(503, text="server busy"),
                FakeResponse(200, payload={"ok": 1}),
            ],
            retries=1,
        )
        with patch("checkin.xiaojuchongdian.src.http.time.sleep") as mock_sleep:
            result = client.post_json("https://example.com", {}, {})

        self.assertEqual(result.data, {"ok": 1})
        self.assertEqual(len(session.calls), 2)
        mock_sleep.assert_called_once()

    def test_post_json_raises_after_retryable_status_exhausted(self) -> None:
        client, _ = self._build_client(
            [
                FakeResponse(503, text="busy-1"),
                FakeResponse(503, text="busy-2"),
            ],
            retries=1,
        )
        with patch("checkin.xiaojuchongdian.src.http.time.sleep"):
            with self.assertRaises(HttpStatusError):
                client.post_json("https://example.com", {}, {})

    def test_post_json_raises_after_request_exception_exhausted(self) -> None:
        client, _ = self._build_client(
            ["request_exception", "request_exception"],
            retries=1,
        )
        with patch("checkin.xiaojuchongdian.src.http.time.sleep"):
            with self.assertRaises(HttpClientError):
                client.post_json("https://example.com", {}, {})

    def test_post_json_raises_status_error_for_non_retryable_4xx(self) -> None:
        client, _ = self._build_client([FakeResponse(400, text="bad request")], retries=0)
        with self.assertRaises(HttpStatusError):
            client.post_json("https://example.com", {}, {})

    def test_post_json_raises_for_invalid_json(self) -> None:
        client, _ = self._build_client(
            [
                FakeResponse(
                    200,
                    text="not json",
                    json_exception=json.JSONDecodeError("invalid", "x", 0),
                )
            ],
            retries=0,
        )
        with self.assertRaises(HttpClientError):
            client.post_json("https://example.com", {}, {})

    def test_short_body_truncates_when_exceeding_limit(self) -> None:
        text = "x" * 210
        short = HttpClient._short_body(text)
        self.assertTrue(short.endswith("..."))
        self.assertEqual(len(short), 203)
