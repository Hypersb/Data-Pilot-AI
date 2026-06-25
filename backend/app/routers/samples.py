from fastapi import APIRouter, HTTPException

from app.schemas.v2_responses import SampleDatasetItem, SampleLoadResponse, SamplesListResponse
from app.services.sample_datasets_service import list_samples, load_sample

router = APIRouter(prefix="/api/samples", tags=["samples"])


@router.get("", response_model=SamplesListResponse)
async def get_samples() -> SamplesListResponse:
    items = [SampleDatasetItem(**s) for s in list_samples()]
    return SamplesListResponse(samples=items, count=len(items))


@router.post("/{sample_id}/load", response_model=SampleLoadResponse)
async def load_sample_dataset(sample_id: str) -> SampleLoadResponse:
    try:
        result = load_sample(sample_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SampleLoadResponse(**result)
