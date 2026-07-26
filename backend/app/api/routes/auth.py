import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)
from app.models.employee import Employee
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.schemas.auth import (
    EmployeeRegisterRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UpdateUserRequest,
    UserResponse,
)
from app.services.audit import record_audit
from app.services.password_reset import (
    deliver_reset_link,
    generate_reset_token,
    hash_reset_token,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
RESET_RESPONSE = (
    "If an account exists for this email, a password-reset link has been sent."
)


def _next_employee_id(db: Session) -> str:
    number = db.query(Employee).count() + 1
    while db.query(Employee).filter(Employee.employee_id == f"EMP{number:03d}").first():
        number += 1
    return f"EMP{number:03d}"


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Legacy admin-only account creation endpoint."""
    if (
        db.query(User)
        .filter(func.lower(User.email) == str(payload.email).lower())
        .first()
    ):
        raise HTTPException(status_code=409, detail="Email already registered")
    if (
        db.query(User)
        .filter(func.lower(User.username) == payload.username.lower())
        .first()
    ):
        raise HTTPException(status_code=409, detail="Username already taken")
    user = User(
        id=uuid.uuid4(),
        email=str(payload.email).lower(),
        username=payload.username,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role="employee",
        is_active=True,
    )
    db.add(user)
    db.flush()
    names = (payload.full_name or payload.username).split(maxsplit=1)
    employee = Employee(
        id=uuid.uuid4(),
        employee_id=_next_employee_id(db),
        user_id=user.id,
        first_name=names[0],
        last_name=names[1] if len(names) > 1 else "",
        email=user.email,
        status="active",
    )
    db.add(employee)
    record_audit(db, current_user, "create", "user", user.id, {"role": "employee"})
    db.commit()
    db.refresh(user)
    return TokenResponse(
        access_token=create_access_token(data={"sub": str(user.id)}), user=user
    )


@router.post(
    "/register-employee",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_employee(payload: EmployeeRegisterRequest, db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    if (
        db.query(User)
        .filter(func.lower(User.username) == payload.username.lower())
        .first()
    ):
        raise HTTPException(status_code=409, detail="Username already taken")

    names = payload.full_name.split(maxsplit=1)
    user = User(
        id=uuid.uuid4(),
        email=email,
        username=payload.username,
        phone=payload.phone or None,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role="employee",
        is_active=True,
        is_superuser=False,
    )
    employee = Employee(
        id=uuid.uuid4(),
        employee_id=_next_employee_id(db),
        user_id=user.id,
        first_name=names[0],
        last_name=names[1] if len(names) > 1 else "",
        email=email,
        phone=payload.phone or None,
        status="active",
    )
    try:
        db.add_all([user, employee])
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Email or username is already registered"
        )
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    identifier = payload.identifier.lower()
    user = (
        db.query(User)
        .filter(
            or_(
                func.lower(User.email) == identifier,
                func.lower(User.username) == identifier,
            )
        )
        .first()
    )
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=401, detail="Invalid email/username or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")

    actual_role = "admin" if user.is_superuser else user.role
    if actual_role != payload.role:
        selected = "Administrator" if payload.role == "admin" else "Employee"
        raise HTTPException(
            status_code=403,
            detail=f"This account is not registered as an {selected}.",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    record_audit(db, user, "login", "authentication")
    db.commit()
    return TokenResponse(access_token=access_token, user=user)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(func.lower(User.email) == str(payload.email).lower())
        .first()
    )
    if user:
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
        recent = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.created_at >= cutoff,
            )
            .first()
        )
        if not recent:
            token, token_hash = generate_reset_token()
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
            )
            db.add(
                PasswordResetToken(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    token_hash=token_hash,
                    expires_at=expires_at,
                )
            )
            db.commit()
            reset_url = (
                f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={token}"
            )
            try:
                deliver_reset_link(user.email, reset_url)
            except Exception:
                # Keep account discovery and mail-provider failures out of the response.
                pass
    return {"message": RESET_RESPONSE}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    record = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == hash_reset_token(payload.token))
        .first()
    )
    if not record or record.used_at is not None:
        raise HTTPException(
            status_code=400, detail="Invalid or already used reset token"
        )
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        raise HTTPException(status_code=400, detail="Password reset token has expired")

    user = db.query(User).filter(User.id == record.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid password reset request")
    user.hashed_password = hash_password(payload.password)
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None),
    ).update({"used_at": now}, synchronize_session=False)
    record_audit(db, user, "password_reset", "authentication")
    db.commit()
    return {"message": "Password reset successful. You can now sign in."}


@router.post("/logout")
def logout(_: User = Depends(get_current_user)):
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    payload: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.email and payload.email != current_user.email:
        if (
            db.query(User)
            .filter(
                func.lower(User.email) == str(payload.email).lower(),
                User.id != current_user.id,
            )
            .first()
        ):
            raise HTTPException(status_code=409, detail="Email already registered")
        current_user.email = str(payload.email).lower()
    if payload.username and payload.username != current_user.username:
        if (
            db.query(User)
            .filter(User.username == payload.username, User.id != current_user.id)
            .first()
        ):
            raise HTTPException(status_code=409, detail="Username already taken")
        current_user.username = payload.username
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.password:
        current_user.hashed_password = hash_password(payload.password)

    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if employee:
        employee.email = current_user.email
        if payload.full_name:
            names = payload.full_name.split(maxsplit=1)
            employee.first_name = names[0]
            employee.last_name = names[1] if len(names) > 1 else ""
    db.commit()
    db.refresh(current_user)
    return current_user
