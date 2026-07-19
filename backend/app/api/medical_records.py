from app.api.users import get_current_user
from app.db.dependencies import get_db

# from app.models.medical_record import MedicalRecord
from app.models.user import Users
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordResponse,
    MedicalRecordUpdate,
)
from app.services.medical_record_service import create_record as create_record_service
from app.services.medical_record_service import delete_record as delete_record_service
from app.services.medical_record_service import get_record, get_user_records
from app.services.medical_record_service import update_record as update_record_service
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# from fastapi import HTTPException


router = APIRouter(prefix="/records", tags=["Medical records"])


@router.post(
    "/",
    response_model=MedicalRecordResponse,
    status_code=201,
    summary="Create a medical record",
    description="Creates a new medical record for the authenticated user.",
    responses={
        201: {"description": "Medical record created successfully"},
        401: {"description": "Authentication required"},
        422: {"description": "Validation error"},
    },
)
def create_record(
    record: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return create_record_service(db=db, user_id=current_user.id, record_data=record)


@router.get(
    "/",
    response_model=list[MedicalRecordResponse],
    summary="List medical records",
    description="Returns all medical records belonging to the authenticated user.",
    responses={
        200: {"description": "Medical records retrieved successfully"},
        401: {"description": "Authentication required"},
    },
)
def get_all_records(
    db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)
):
    return get_user_records(db=db, user_id=current_user.id)


@router.get(
    "/{record_id}",
    response_model=MedicalRecordResponse,
    summary="Get a medical record",
    description="Returns a single medical record owned by the authenticated user.",
    responses={
        200: {"description": "Medical record retrieved successfully"},
        401: {"description": "Authentication required"},
        404: {"description": "Medical record not found"},
    },
)
def get_records(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return get_record(db=db, record_id=record_id, user_id=current_user.id)


@router.put(
    "/{record_id}",
    response_model=MedicalRecordResponse,
    summary="Update a medical record",
    description="Updates an existing medical record owned by the authenticated user.",
    responses={
        200: {"description": "Medical record updated successfully"},
        401: {"description": "Authentication required"},
        404: {"description": "Medical record not found"},
        422: {"description": "Validation error"},
    },
)
def update_record(
    record_id: int,
    updated_record: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    record = get_record(db=db, record_id=record_id, user_id=current_user.id)

    return update_record_service(db=db, record=record, updated_data=updated_record)


@router.delete(
    "/{record_id}",
    summary="Delete a medical record",
    description="Deletes a medical record owned by the authenticated user.",
    responses={
        200: {"description": "Medical record deleted successfully"},
        401: {"description": "Authentication required"},
        404: {"description": "Medical record not found"},
    },
)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    record = get_record(db=db, record_id=record_id, user_id=current_user.id)

    return delete_record_service(db=db, record=record)
