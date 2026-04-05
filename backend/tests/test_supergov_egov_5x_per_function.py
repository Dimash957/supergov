from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, Iterator, List, Tuple, get_args, get_origin

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.main import app
from app.routers import egov as egov_router


# Helpers


def _async_return(value: Any):
    async def _fn(*args, **kwargs):
        return value

    return _fn


def _async_raise(*args, **kwargs):
    raise RuntimeError("forced test failure")


class _FakeQuery:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def execute(self):
        if self.table_name == "documents":
            return SimpleNamespace(data=[{"id": "DOC1", "name": "Passport"}])
        if self.table_name == "applications":
            return SimpleNamespace(data=[{"id": "APP1", "status": "processing"}])
        return SimpleNamespace(data=[])


class _FakeDB:
    def table(self, table_name: str):
        return _FakeQuery(table_name)


def _fake_db_raise():
    raise RuntimeError("forced database failure")


def _sample_value(name: str, annotation: Any = None) -> Any:
    by_name: Dict[str, Any] = {
        "service_type": "PASSPORT",
        "iin": "870412300415",
        "email": "test@example.com",
        "phone": "+77000000000",
        "full_name": "Test User",
        "ref_number": "REF123",
        "document_id": "DOC123",
        "service_id": "PASSPORT",
        "application_id": "APP123",
        "doc_type": "passport",
        "contact_type": "email",
        "value": "test@example.com",
        "otp": "123456",
        "token": "token123",
        "issue_title": "Test issue",
        "issue_description": "Issue details",
        "severity": "normal",
        "currency": "KZT",
        "file_path": "/tmp/doc.pdf",
        "notification_id": "N1",
        "category": "documents",
    }
    if name in by_name:
        return by_name[name]

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in (list, List):
        subtype = args[0] if args else str
        return [_sample_value(f"{name}_item", subtype)]
    if origin in (dict, Dict):
        return {}

    if annotation is dict:
        return {}
    if annotation is list:
        return ["x"]
    if annotation is int:
        return 1
    if annotation is float:
        return 100.0
    if annotation is bool:
        return True

    return "test"


def _is_required(field: Any) -> bool:
    if hasattr(field, "required"):
        return bool(getattr(field, "required"))
    if hasattr(field, "default"):
        default = getattr(field, "default")
        if default is not None and repr(default) == "PydanticUndefined":
            return True
    if hasattr(field, "field_info"):
        finfo = getattr(field, "field_info")
        if hasattr(finfo, "is_required"):
            fn = getattr(finfo, "is_required")
            return bool(fn() if callable(fn) else fn)
        if hasattr(finfo, "required"):
            return bool(getattr(finfo, "required"))
    if hasattr(field, "is_required"):
        flag = getattr(field, "is_required")
        return bool(flag() if callable(flag) else flag)
    return False


def _annotation_of(field: Any) -> Any:
    if hasattr(field, "annotation"):
        return getattr(field, "annotation")
    if hasattr(field, "field_info") and hasattr(field.field_info, "annotation"):
        return getattr(field.field_info, "annotation")
    if hasattr(field, "type_"):
        return getattr(field, "type_")
    return None


def _route_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for route in egov_router.router.routes:
        if not isinstance(route, APIRoute):
            continue
        methods = sorted(m for m in route.methods if m not in {"HEAD", "OPTIONS"})
        for method in methods:
            cases.append(
                {
                    "name": route.name,
                    "method": method,
                    "path": route.path,
                    "route": route,
                }
            )
    return cases


def _build_path(path_template: str) -> str:
    path = path_template
    for segment in path_template.split("/"):
        if segment.startswith("{") and segment.endswith("}"):
            key = segment[1:-1]
            path = path.replace("{" + key + "}", str(_sample_value(key)))
    return path


def _build_request_payload(route: APIRoute) -> Tuple[Dict[str, Any], Any]:
    params: Dict[str, Any] = {}
    body: Dict[str, Any] = {}

    for qp in route.dependant.query_params:
        if _is_required(qp):
            params[qp.name] = _sample_value(qp.name, _annotation_of(qp))

    required_body_params = [bp for bp in route.dependant.body_params if _is_required(bp)]
    if len(required_body_params) == 1:
        only_bp = required_body_params[0]
        ann = _annotation_of(only_bp)
        if get_origin(ann) in (list, List):
            return params, _sample_value(only_bp.name, ann)

    for bp in required_body_params:
        body[bp.name] = _sample_value(bp.name, _annotation_of(bp))

    return params, body


def _required_non_path_count(route: APIRoute) -> int:
    required_query = sum(1 for p in route.dependant.query_params if _is_required(p))
    required_body = sum(1 for p in route.dependant.body_params if _is_required(p))
    return required_query + required_body


def _invoke(client: TestClient, method: str, path: str, params: Dict[str, Any], body: Dict[str, Any]):
    kwargs: Dict[str, Any] = {}
    if params:
        kwargs["params"] = params
    if body:
        kwargs["json"] = body
    return client.request(method, path, **kwargs)


ROUTE_CASES = _route_cases()
CASE_IDS = [f"{c['method']} {c['path']} :: {c['name']}" for c in ROUTE_CASES]


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    # Override auth once for deterministic tests.
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "user-1",
        "email": "user@example.com",
        "iin": "870412300415",
        "name": "Test User",
    }

    # Patch DB helper used by /my-documents and /my-applications.
    monkeypatch.setattr(egov_router, "get_db", lambda: _FakeDB())

    # Patch connector methods used by eGov routes.
    async_map = {
        "healthcheck": True,
        "get_api_version": "1.0.0",
        "get_status": {"status": "ok"},
        "reset_cache": None,
        "get_services": [{"id": "PASSPORT"}],
        "search_services": [{"id": "PASSPORT", "name": "Passport"}],
        "get_services_by_category": [{"id": "PASSPORT"}],
        "get_service_by_id": {"id": "PASSPORT", "name": "Passport"},
        "get_service_requirements": ["iin", "photo"],
        "get_service_documents": ["passport_copy"],
        "get_service_cost": {"amount": 1000, "currency": "KZT"},
        "get_service_processing_time": "3 days",
        "get_service_offices": [{"id": "office-1"}],
        "get_service_faq": [{"q": "How?", "a": "Like this"}],
        "submit_application": {"ref_number": "REF123", "status": "submitted"},
        "check_application_status": {"status": "processing"},
        "get_application_details": {"ref_number": "REF123", "details": {}},
        "cancel_application": True,
        "resubmit_application": {"ref_number": "REF123", "status": "resubmitted"},
        "get_application_history": [{"ref_number": "REF123"}],
        "get_application_steps": [{"step": 1, "name": "Created"}],
        "upload_application_document": True,
        "poll_application_status": {"status": "completed"},
        "batch_check_applications": [{"ref_number": "REF123", "status": "ok"}],
        "get_documents": [{"id": "DOC123"}],
        "get_document_by_id": {"id": "DOC123", "type": "passport"},
        "verify_document": {"verified": True},
        "download_document": b"PDFDATA",
        "get_document_status": "active",
        "renew_document": True,
        "get_document_template": {"template": "standard"},
        "validate_document_data": (True, "ok"),
        "request_document_copy": True,
        "get_document_history": [{"action": "created"}],
        "get_user_profile": {"iin": "870412300415", "name": "Test User"},
        "update_user_contact": True,
        "verify_user_phone": True,
        "verify_user_email": True,
        "get_user_notifications": [{"id": "N1", "read": False}],
        "mark_notification_read": True,
        "get_user_preferences": {"language": "ru"},
        "update_user_preferences": True,
        "get_user_subscriptions": [{"service_id": "PASSPORT"}],
        "subscribe_to_service": True,
        "get_payment_info": {"application_id": "APP123", "amount": 1000},
        "initiate_payment": {"payment_id": "PAY1", "status": "initiated"},
        "get_analytics": {"total": 10},
        "get_system_load": {"cpu": 10, "memory": 40},
        "report_issue": True,
    }
    sync_map = {
        "get_stats": {"requests": 1, "success": 1},
    }

    for method_name, value in async_map.items():
        monkeypatch.setattr(egov_router.egov_connector, method_name, _async_return(value))
    for method_name, value in sync_map.items():
        monkeypatch.setattr(egov_router.egov_connector, method_name, lambda value=value: value)

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.parametrize("case", ROUTE_CASES, ids=CASE_IDS)
def test_1_route_registered(case: Dict[str, Any]):
    # Test #1 for each function: route metadata exists and is callable.
    route = case["route"]
    assert case["path"].startswith("/api/egov")
    assert case["method"] in route.methods
    assert callable(route.endpoint)


@pytest.mark.parametrize("case", ROUTE_CASES, ids=CASE_IDS)
def test_2_wrong_method_returns_405(client: TestClient, case: Dict[str, Any]):
    # Test #2 for each function: unsupported HTTP method is rejected.
    path = _build_path(case["path"])
    wrong_method = "DELETE" if case["method"] != "DELETE" else "PATCH"
    resp = client.request(wrong_method, path)
    assert resp.status_code == 405


@pytest.mark.parametrize("case", ROUTE_CASES, ids=CASE_IDS)
def test_3_missing_required_inputs_validation(client: TestClient, case: Dict[str, Any]):
    # Test #3 for each function: required params/body are validated.
    path = _build_path(case["path"])
    resp = client.request(case["method"], path)

    required_non_path = _required_non_path_count(case["route"])
    if required_non_path > 0:
        assert resp.status_code == 422
    else:
        assert resp.status_code != 422


@pytest.mark.parametrize("case", ROUTE_CASES, ids=CASE_IDS)
def test_4_happy_path_smoke(client: TestClient, case: Dict[str, Any]):
    # Test #4 for each function: minimal valid request works without 5xx.
    path = _build_path(case["path"])
    params, body = _build_request_payload(case["route"])
    resp = _invoke(client, case["method"], path, params, body)

    assert resp.status_code < 500


@pytest.mark.parametrize("case", ROUTE_CASES, ids=CASE_IDS)
def test_5_backend_failure_handling(client: TestClient, monkeypatch: pytest.MonkeyPatch, case: Dict[str, Any]):
    # Test #5 for each function: backend/connector failures are handled.
    # get_profile uses only dependency-injected user and should not fail when connector/db fails.
    non_external_endpoint_names = {"get_profile"}

    # Fail DB access.
    monkeypatch.setattr(egov_router, "get_db", _fake_db_raise)

    # Fail connector methods.
    for attr in dir(egov_router.egov_connector):
        if attr.startswith("_"):
            continue
        value = getattr(egov_router.egov_connector, attr)
        if callable(value):
            if attr == "get_stats":
                monkeypatch.setattr(egov_router.egov_connector, attr, lambda: (_ for _ in ()).throw(RuntimeError("forced test failure")))
            else:
                monkeypatch.setattr(egov_router.egov_connector, attr, _async_raise)

    path = _build_path(case["path"])
    params, body = _build_request_payload(case["route"])
    resp = _invoke(client, case["method"], path, params, body)

    if case["name"] in non_external_endpoint_names:
        assert resp.status_code < 500
    else:
        assert 500 <= resp.status_code < 600
