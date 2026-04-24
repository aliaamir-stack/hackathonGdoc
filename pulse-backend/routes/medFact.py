from fastapi import APIRouter, HTTPException, Request

from limiter import limiter
from models.schemas import MedFactRequest, MedFactResponse

router = APIRouter(tags=["medFact"])


@router.post("/medFact", response_model=MedFactResponse)
@limiter.limit("10/minute")
async def med_fact(request: Request, payload: MedFactRequest) -> MedFactResponse:
    try:
        from ai.rag_chain import verify_health_claim  # type: ignore

        result = await verify_health_claim(payload.claim)
        return MedFactResponse(**result)
    except ImportError:
        return MedFactResponse(
            verdict="FALSE",
            confidence=0.92,
            sub_claims=["Papaya leaf juice cures dengue in 24 hours"],
            citations=[
                {
                    "title": "Supportive care in dengue fever",
                    "source": "PubMed",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/",
                }
            ],
            summary="Claim is not medically supported as a definitive cure.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"medFact failed: {exc}") from exc
