from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.dependencies import get_db
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.user import User
from app.schemas.diagnostic import (
    DiagnosticCentreCreate,
    DiagnosticCentreResponse,
)


router = APIRouter(prefix="/diagnostic-centres", tags=["Diagnostic Centres"])


@router.post(
    "/",
    response_model=DiagnosticCentreResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_centre(
    centre_data: DiagnosticCentreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    centre = DiagnosticCentre(
        name=centre_data.name,
        location=centre_data.location,
    )

    db.add(centre)
    db.commit()
    db.refresh(centre)

    return centre


@router.get("/", response_model=list[DiagnosticCentreResponse])
def get_centres(db: Session = Depends(get_db)):
    return (
        db.query(DiagnosticCentre)
        .filter(DiagnosticCentre.is_active.is_(True))
        .all()
    )

from app.models.diagnostic_test import DiagnosticTest
from app.schemas.diagnostic import (
    DiagnosticTestCreate,
    DiagnosticTestResponse,
)


@router.post(
    "/tests/",
    response_model=DiagnosticTestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_test(
    test_data: DiagnosticTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_test = (
        db.query(DiagnosticTest)
        .filter(DiagnosticTest.name == test_data.name)
        .first()
    )

    if existing_test:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Diagnostic test already exists",
        )

    test = DiagnosticTest(
        name=test_data.name,
        description=test_data.description,
    )

    db.add(test)
    db.commit()
    db.refresh(test)

    return test


@router.get("/tests/", response_model=list[DiagnosticTestResponse])
def get_tests(db: Session = Depends(get_db)):
    return db.query(DiagnosticTest).all()

from app.models.centre_test import CentreTest
from app.schemas.diagnostic import (
    CentreTestCreate,
    CentreTestResponse,
)


@router.post(
    "/centre-tests/",
    response_model=CentreTestResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_test_to_centre(
    data: CentreTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    centre = (
        db.query(DiagnosticCentre)
        .filter(DiagnosticCentre.id == data.centre_id)
        .first()
    )

    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )

    test = (
        db.query(DiagnosticTest)
        .filter(DiagnosticTest.id == data.test_id)
        .first()
    )

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found",
        )

    centre_test = CentreTest(
        centre_id=data.centre_id,
        test_id=data.test_id,
        price=data.price,
    )

    db.add(centre_test)
    db.commit()
    db.refresh(centre_test)

    return centre_test