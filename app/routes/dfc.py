from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from sqlmodel import Session, select
from ..models.dfc import DFC
from ..models.reference import Reference
from ..schemas.dfc import DFCCreate, DFCRead
from ..core.security import get_current_user
from ..core.exceptions import ValidationError, NotFoundError, InternalServerError
from .. import database
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dfcs", tags=["dfcs"])


@router.post("/", response_model=DFCRead, status_code=status.HTTP_201_CREATED)
def create_dfc(dfc_in: DFCCreate, current_user=Depends(get_current_user), session: Session = Depends(database.get_session)):
    """Create a new DFC. Requires authentication."""
    try:
        if not dfc_in.numero_dfc:
            raise ValidationError("numero_dfc is required")

        # Check for duplicates
        existing = session.exec(
            select(DFC).where(DFC.numero_dfc == dfc_in.numero_dfc)
        ).first()
        if existing:
            raise ValidationError(f"DFC with numero {dfc_in.numero_dfc} already exists")

        # Prepare data and resolve textual references to FK ids
        payload = dfc_in.model_dump(exclude_unset=True)

        def _resolve_ref(name: str, ref_type: str) -> Optional[int]:
            if not name:
                return None
            ref = session.exec(
                select(Reference).where(Reference.name == name, Reference.type == ref_type)
            ).first()
            if not ref:
                ref = Reference(name=name, type=ref_type)
                session.add(ref)
                session.commit()
                session.refresh(ref)
            return ref.id

        # map text fields to *_id
        if "projet" in payload:
            projet_name = payload.pop("projet")
            payload["projet_id"] = _resolve_ref(projet_name, "project")
        if "famille" in payload:
            famille_name = payload.pop("famille")
            payload["famille_id"] = _resolve_ref(famille_name, "family")
        if "phase" in payload:
            phase_name = payload.pop("phase")
            payload["phase_id"] = _resolve_ref(phase_name, "phase")

        # Use pydantic v2 style validation for SQLModel
        dfc = DFC.model_validate(payload)
        session.add(dfc)
        session.commit()
        session.refresh(dfc)
        logger.info(f"DFC created: {dfc.id} by user {current_user.matricule}")
        return dfc
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error creating DFC: {str(e)}", exc_info=True)
        raise InternalServerError("Failed to create DFC")


@router.get("/", response_model=list[DFCRead])
def list_dfcs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    statut: str = Query(None),
    current_user=Depends(get_current_user),
    session: Session = Depends(database.get_session)
):
    """List DFCs with pagination and filtering. Requires authentication."""
    try:
        query = select(DFC)

        if statut:
            if statut not in ["ouvert", "ferme"]:
                raise ValidationError("Invalid statut. Must be 'ouvert' or 'ferme'")
            query = query.where(DFC.statut == statut)

        dfcs = session.exec(query.offset(skip).limit(limit)).all()
        logger.info(f"Listed {len(dfcs)} DFCs by user {current_user.matricule}")
        return dfcs
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error listing DFCs: {str(e)}", exc_info=True)
        raise InternalServerError("Failed to list DFCs")


@router.get("/{dfc_id}", response_model=DFCRead)
def get_dfc(dfc_id: int, current_user=Depends(get_current_user), session: Session = Depends(database.get_session)):
    """Get a specific DFC. Requires authentication."""
    try:
        dfc = session.get(DFC, dfc_id)
        if not dfc:
            raise NotFoundError("DFC")
        logger.info(f"Retrieved DFC {dfc_id} by user {current_user.matricule}")
        return dfc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving DFC {dfc_id}: {str(e)}", exc_info=True)
        raise InternalServerError("Failed to retrieve DFC")


@router.put("/{dfc_id}", response_model=DFCRead)
def update_dfc(
    dfc_id: int,
    dfc_in: DFCCreate,
    current_user=Depends(get_current_user),
    session: Session = Depends(database.get_session)
):
    """Update a DFC. Requires authentication."""
    try:
        dfc = session.get(DFC, dfc_id)
        if not dfc:
            raise NotFoundError("DFC")

        # Update only provided fields (Pydantic v2)
        payload = dfc_in.model_dump(exclude_unset=True)

        # map textual references to FK ids for update
        if "projet" in payload:
            projet_name = payload.pop("projet")
            proj_ref = session.exec(
                select(Reference).where(Reference.name == projet_name, Reference.type == "project")
            ).first()
            if proj_ref:
                payload["projet_id"] = proj_ref.id
            else:
                # create new reference
                ref = Reference(name=projet_name, type="project")
                session.add(ref)
                session.commit()
                session.refresh(ref)
                payload["projet_id"] = ref.id
        if "famille" in payload:
            famille_name = payload.pop("famille")
            fam_ref = session.exec(
                select(Reference).where(Reference.name == famille_name, Reference.type == "family")
            ).first()
            if fam_ref:
                payload["famille_id"] = fam_ref.id
            else:
                ref = Reference(name=famille_name, type="family")
                session.add(ref)
                session.commit()
                session.refresh(ref)
                payload["famille_id"] = ref.id
        if "phase" in payload:
            phase_name = payload.pop("phase")
            ph_ref = session.exec(
                select(Reference).where(Reference.name == phase_name, Reference.type == "phase")
            ).first()
            if ph_ref:
                payload["phase_id"] = ph_ref.id
            else:
                ref = Reference(name=phase_name, type="phase")
                session.add(ref)
                session.commit()
                session.refresh(ref)
                payload["phase_id"] = ref.id

        for k, v in payload.items():
            setattr(dfc, k, v)

        session.add(dfc)
        session.commit()
        session.refresh(dfc)
        logger.info(f"Updated DFC {dfc_id} by user {current_user.matricule}")
        return dfc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating DFC {dfc_id}: {str(e)}", exc_info=True)
        raise InternalServerError("Failed to update DFC")


@router.delete("/{dfc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dfc(dfc_id: int, current_user=Depends(get_current_user), session: Session = Depends(database.get_session)):
    """Delete a DFC. Requires authentication."""
    try:
        dfc = session.get(DFC, dfc_id)
        if not dfc:
            raise NotFoundError("DFC")

        session.delete(dfc)
        session.commit()
        logger.info(f"Deleted DFC {dfc_id} by user {current_user.matricule}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting DFC {dfc_id}: {str(e)}", exc_info=True)
        raise InternalServerError("Failed to delete DFC")
