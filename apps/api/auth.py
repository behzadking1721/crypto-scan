from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register():
    return {"status": "not implemented"}


@router.post("/login")
def login():
    return {"status": "not implemented"}


@router.post("/oauth/google")
def oauth_google():
    return {"status": "not implemented"}
