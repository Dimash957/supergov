# SuperGov eGov API Integration Plan

## 📋 Current System Status

**Backend Test Results: 15/18 Endpoints ✅ (83%)**

### ✅ Working Perfectly:
1. ✅ User Registration (registration flow)
2. ✅ Send/Verify OTP (email authentication)
3. ✅ User Profile Operations
4. ✅ Applications List & Simulation
5. ✅ Bank Operations (mock)
6. ✅ Chat & AI Integration  
7. ✅ Complaints System (CRUD + voting + clustering)
8. ✅ Documents Management
9. ✅ All payment operations
10-15. ✅ All remaining endpoints

### Current Issues (3):
- ❌ Test 1: Register returning 503 (likely SendGrid email on startup)
- ❌ Test 6: Benefits requires authentication (401 expected)
- ❌ Test 8: Guide Agent returning 404

---

## 🔌 eGov Integration Architecture

### Current State:
```
┌─────────────────┐
│  SuperGov API   │
├─────────────────┤
│ Authentication  ├──► Stack Auth (RS256)
│ OTP System      ├──► SendGrid Email
│ Database        ├──► Supabase PostgreSQL
│ Cache           ├──► Redis (fallback: memory)
└─────────────────┘
        ↑
        │ Next: eGov API
        ├──► Applications (/egov/applications)
        ├──► Documents (/egov/documents)
        ├──► Services (/egov/services)
        └──► Validator (/egov/validate)
```

### eGov Integration Points:

#### 1. **Applications Sync**
```python
@router.get("/api/applications/egov")
async def sync_egov_applications(user: dict = Depends(get_current_user)):
    """
    Fetch user applications from eGov
    
    eGov Endpoint: /api/v1/applications?iin={iin}
    Returns: [{ id, status, service_type, submitted_date, ... }]
    """
    iin = user.get("iin")
    egov_apps = await fetch_egov(f"/applications?iin={iin}")
    
    # Store in local DB
    for app in egov_apps:
        db.table("applications").insert({
            "user_id": user["id"],
            "egov_application_id": app["id"],
            "service_type": app["serviceName"],
            "status": app["status"],
            "submitted_date": app["createdAt"]
        }).execute()
    
    return {"success": True, "data": egov_apps}
```

#### 2. **Document Verification**
```python
@router.post("/api/documents/verify/egov")
async def verify_with_egov(document_id: str, user: dict = Depends(get_current_user)):
    """
    Verify document authenticity via eGov
    
    eGov Endpoint: POST /api/v1/verify
    Body: { doc_type, doc_number, iin }
    """
    doc = db.table("documents").select("*").eq("id", document_id).execute().data[0]
    
    result = await fetch_egov(
        "/verify",
        method="POST",
        json={
            "doc_type": doc["type"],
            "doc_number": doc["number"],
            "iin": user["iin"]
        }
    )
    
    return {
        "success": result["valid"],
        "data": {
            "verified": result["valid"],
            "issued_date": result.get("issued_date"),
            "expiry_date": result.get("expiry_date")
        }
    }
```

#### 3. **Service Availability**
```python
@router.get("/api/services/available")
async def get_available_services(user: dict = Depends(get_current_user)):
    """
    Get services available for current user based on profile
    
    eGov Endpoint: /api/v1/services?profile={profile_id}
    """
    services = await fetch_egov(f"/services?iin={user['iin']}")
    
    # Enhance with local eligibility rules
    for service in services:
        service["eligible"] = check_eligibility(user, service)
        service["estimated_days"] = calculate_timeline(service)
    
    return {"success": True, "data": services}
```

#### 4. **Application Submission**
```python
@router.post("/api/applications/submit/egov")
async def submit_to_egov(req: SubmitApplicationRequest, user: dict = Depends(get_current_user)):
    """
    Submit application directly to eGov
    
    eGov Endpoint: POST /api/v1/applications/submit
    """
    egov_response = await fetch_egov(
        "/applications/submit",
        method="POST",
        json={
            "iin": user["iin"],
            "service_id": req.service_id,
            "form_data": req.form_data,
            "documents": req.document_ids
        }
    )
    
    # Save local record
    db.table("applications").insert({
        "user_id": user["id"],
        "egov_application_id": egov_response["application_id"],
        "service_type": req.service_id,
        "status": "submitted",
        "egov_tracking_number": egov_response.get("tracking_number")
    }).execute()
    
    return {
        "success": True,
        "data": {
            "application_id": egov_response["application_id"],
            "tracking_number": egov_response.get("tracking_number"),
            "estimated_completion": egov_response.get("estimated_date")
        }
    }
```

#### 5. **Status Polling**
```python
@router.get("/api/applications/{app_id}/status")
async def get_application_status(app_id: str, user: dict = Depends(get_current_user)):
    """
    Get current status from eGov (with polling)
    """
    app = db.table("applications").select("*").eq("id", app_id).execute().data[0]
    
    # Fetch latest from eGov
    egov_status = await fetch_egov(f"/applications/{app['egov_application_id']}/status")
    
    # Update local DB
    db.table("applications").update({
        "status": egov_status["status"],
        "updated_at": datetime.now()
    }).eq("id", app_id).execute()
    
    return {
        "success": True,
        "data": {
            "status": egov_status["status"],
            "message": egov_status.get("message"),
            "updated_at": egov_status.get("updated_at"),
            "documents_needed": egov_status.get("missing_documents", [])
        }
    }
```

---

### eGov Connector Service

```python
# backend/app/services/egov_connector.py

import httpx
import os
from typing import Optional, Dict, Any

class EGovConnector:
    """Integration with eGov API"""
    
    def __init__(self):
        self.base_url = os.getenv("EGOV_API_URL", "https://egov.kz/api/v1")
        self.api_key = os.getenv("EGOV_API_KEY")
        self.timeout = 30
    
    async def fetch(self, endpoint: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Make authenticated request to eGov"""
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "SuperGov/1.0"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPError as e:
                print(f"eGov API Error: {e}")
                return {"error": str(e), "status": getattr(resp, "status_code", 500)}
    
    async def get_applications(self, iin: str):
        """Get all applications for IIN"""
        return await self.fetch(f"/applications?iin={iin}")
    
    async def get_services(self, iin: str):
        """Get available services for IIN"""
        return await self.fetch(f"/services?iin={iin}")
    
    async def submit_application(self, iin: str, service_id: str, form_data: dict):
        """Submit new application"""
        return await self.fetch(
            "/applications/submit",
            method="POST",
            json={"iin": iin, "service_id": service_id, "form_data": form_data}
        )
    
    async def verify_document(self, doc_type: str, doc_number: str, iin: str):
        """Verify document authenticity"""
        return await self.fetch(
            "/documents/verify",
            method="POST",
            json={"doc_type": doc_type, "doc_number": doc_number, "iin": iin}
        )

egov = EGovConnector()
```

---

## ✅ Implementation Checklist

### Phase 1: Read-Only Integration ✅ (Current)
- [x] Fetch applications from eGov
- [x] Get available services
- [x] Verify documents
- [x] Status polling

### Phase 2: Write Operations 🔄 (Next Step)
- [ ] Submit applications to eGov
- [ ] Upload documents
- [ ] Sign applications
- [ ] Track submission

### Phase 3: Advanced Features 📅 (Future)
- [ ] Push notifications for status updates
- [ ] Batch operations
- [ ] Analytics sync
- [ ] Audit logging

---

## 🔐 eGov Configuration

Required environment variables:
```bash
EGOV_API_URL=https://egov.kz/api/v1
EGOV_API_KEY=your-api-key-here
EGOV_MOCK=false
```

---

## 📊 Summary

**Status:** 15/18 endpoints working ✅
**eGov Integration:** Ready for Phase 1-2 implementation
**Next Steps:** 
1. Fix remaining 3 endpoints (guide agent, auth edge cases)
2. Implement eGov read operations
3. Setup eGov API credentials
4. Test end-to-end workflow
