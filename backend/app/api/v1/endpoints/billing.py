"""Billing API endpoints for subscription and payment management."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.utils.database import get_db
from app.models import (
    BillingAccount, BillingEvent, BillingStatus, BillingEventType, BlockReason
)
from app.schemas.common import APIResponse
from app.dependencies import get_current_user, CurrentUser

router = APIRouter()


# ============== Schemas ==============

class BillingSummaryResponse(BaseModel):
    """Billing summary response."""
    status: BillingStatus
    has_payment_method: bool
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    card_exp_month: Optional[str] = None
    card_exp_year: Optional[str] = None
    trial_active: bool
    trial_ends_at: Optional[datetime] = None
    subscription_active: bool
    subscription_plan: Optional[str] = None
    credits_balance: int
    runs_remaining: int
    can_run_analysis: bool
    block_reason: Optional[BlockReason] = None


class PaymentMethodAdd(BaseModel):
    """Payment method add request (mock - never store full PAN)."""
    card_number: str = Field(..., min_length=13, max_length=19)
    exp_month: str = Field(..., min_length=1, max_length=2)
    exp_year: str = Field(..., min_length=2, max_length=4)
    cvv: str = Field(..., min_length=3, max_length=4)
    cardholder_name: str = Field(..., min_length=1)


class CreditsPurchase(BaseModel):
    """Credits purchase request."""
    amount: int = Field(..., ge=1)


# ============== Helper Functions ==============

def get_or_create_billing_account(db: Session, workspace_id) -> BillingAccount:
    """Get existing billing account or create a new one."""
    billing = db.query(BillingAccount).filter(
        BillingAccount.workspace_id == workspace_id
    ).first()

    if not billing:
        billing = BillingAccount(
            workspace_id=workspace_id,
            status=BillingStatus.UNINITIALIZED,
            has_payment_method=False,
            trial_active=False,
            subscription_active=False,
            credits_balance=0,
            runs_remaining=0,
        )
        db.add(billing)
        db.commit()
        db.refresh(billing)

    return billing


def log_billing_event(
    db: Session,
    billing_account_id,
    event_type: BillingEventType,
    user_id=None,
    description: str = None,
    event_metadata: dict = None,
):
    """Log a billing event."""
    event = BillingEvent(
        billing_account_id=billing_account_id,
        event_type=event_type,
        user_id=user_id,
        description=description,
        event_metadata=event_metadata,
    )
    db.add(event)
    db.commit()


# ============== Endpoints ==============

@router.get("/summary", response_model=APIResponse[BillingSummaryResponse])
async def get_billing_summary(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get billing summary for current workspace."""
    if not current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No workspace associated with user",
        )

    billing = get_or_create_billing_account(db, current_user.workspace_id)

    # Check if can run analysis
    can_run, block_reason = billing.can_run_analysis()

    return APIResponse(
        success=True,
        data=BillingSummaryResponse(
            status=billing.status,
            has_payment_method=billing.has_payment_method,
            card_last4=billing.card_last4,
            card_brand=billing.card_brand,
            card_exp_month=billing.card_exp_month,
            card_exp_year=billing.card_exp_year,
            trial_active=billing.trial_active,
            trial_ends_at=billing.trial_ends_at,
            subscription_active=billing.subscription_active,
            subscription_plan=billing.subscription_plan,
            credits_balance=billing.credits_balance,
            runs_remaining=billing.runs_remaining,
            can_run_analysis=can_run,
            block_reason=block_reason,
        )
    )


@router.post("/trial/start", response_model=APIResponse[BillingSummaryResponse])
async def start_trial(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a free trial."""
    if not current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No workspace associated with user",
        )

    billing = get_or_create_billing_account(db, current_user.workspace_id)

    # Check if trial already used
    if billing.trial_started_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trial has already been used for this workspace",
        )

    # Require payment method first
    if not billing.has_payment_method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please add a payment method before starting trial",
        )

    # Start trial
    billing.trial_active = True
    billing.trial_started_at = datetime.utcnow()
    billing.trial_ends_at = datetime.utcnow() + timedelta(days=14)  # 14-day trial
    billing.status = BillingStatus.TRIAL_ACTIVE
    billing.runs_remaining = 10  # 10 analysis runs during trial

    db.commit()
    db.refresh(billing)

    # Log event
    log_billing_event(
        db,
        billing.id,
        BillingEventType.TRIAL_STARTED,
        current_user.id,
        "14-day free trial started",
        {"trial_ends_at": billing.trial_ends_at.isoformat()},
    )

    can_run, block_reason = billing.can_run_analysis()

    return APIResponse(
        success=True,
        data=BillingSummaryResponse(
            status=billing.status,
            has_payment_method=billing.has_payment_method,
            card_last4=billing.card_last4,
            card_brand=billing.card_brand,
            card_exp_month=billing.card_exp_month,
            card_exp_year=billing.card_exp_year,
            trial_active=billing.trial_active,
            trial_ends_at=billing.trial_ends_at,
            subscription_active=billing.subscription_active,
            subscription_plan=billing.subscription_plan,
            credits_balance=billing.credits_balance,
            runs_remaining=billing.runs_remaining,
            can_run_analysis=can_run,
            block_reason=block_reason,
        )
    )


@router.post("/payment-method/mock-add", response_model=APIResponse[BillingSummaryResponse])
async def add_payment_method(
    data: PaymentMethodAdd,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a payment method (mock implementation).

    IMPORTANT: This is a mock endpoint for development.
    In production, use Stripe or another payment processor.
    Never store full card numbers or CVV.
    """
    if not current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No workspace associated with user",
        )

    billing = get_or_create_billing_account(db, current_user.workspace_id)

    # Validate card number (basic Luhn check would go here in production)
    card_number = data.card_number.replace(" ", "").replace("-", "")
    if not card_number.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid card number",
        )

    # Determine card brand from prefix
    card_brand = "unknown"
    if card_number.startswith("4"):
        card_brand = "visa"
    elif card_number.startswith(("51", "52", "53", "54", "55")):
        card_brand = "mastercard"
    elif card_number.startswith(("34", "37")):
        card_brand = "amex"
    elif card_number.startswith("6011"):
        card_brand = "discover"

    # Store only last 4 digits and metadata (NEVER store full PAN or CVV)
    billing.has_payment_method = True
    billing.card_last4 = card_number[-4:]
    billing.card_brand = card_brand
    billing.card_exp_month = data.exp_month.zfill(2)
    billing.card_exp_year = data.exp_year if len(data.exp_year) == 4 else f"20{data.exp_year}"

    # Update status
    if billing.status == BillingStatus.UNINITIALIZED:
        billing.status = BillingStatus.PAYMENT_METHOD_REQUIRED  # Still need trial or subscription

    db.commit()
    db.refresh(billing)

    # Log event
    log_billing_event(
        db,
        billing.id,
        BillingEventType.PAYMENT_METHOD_ADDED,
        current_user.id,
        f"Payment method added: {card_brand} ****{billing.card_last4}",
        {"brand": card_brand, "last4": billing.card_last4},
    )

    can_run, block_reason = billing.can_run_analysis()

    return APIResponse(
        success=True,
        data=BillingSummaryResponse(
            status=billing.status,
            has_payment_method=billing.has_payment_method,
            card_last4=billing.card_last4,
            card_brand=billing.card_brand,
            card_exp_month=billing.card_exp_month,
            card_exp_year=billing.card_exp_year,
            trial_active=billing.trial_active,
            trial_ends_at=billing.trial_ends_at,
            subscription_active=billing.subscription_active,
            subscription_plan=billing.subscription_plan,
            credits_balance=billing.credits_balance,
            runs_remaining=billing.runs_remaining,
            can_run_analysis=can_run,
            block_reason=block_reason,
        )
    )


@router.delete("/payment-method", response_model=APIResponse)
async def remove_payment_method(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove the payment method."""
    if not current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No workspace associated with user",
        )

    billing = get_or_create_billing_account(db, current_user.workspace_id)

    if not billing.has_payment_method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No payment method to remove",
        )

    # Cannot remove if subscription is active
    if billing.subscription_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove payment method while subscription is active",
        )

    old_card = f"{billing.card_brand} ****{billing.card_last4}"

    billing.has_payment_method = False
    billing.card_last4 = None
    billing.card_brand = None
    billing.card_exp_month = None
    billing.card_exp_year = None

    db.commit()

    # Log event
    log_billing_event(
        db,
        billing.id,
        BillingEventType.PAYMENT_METHOD_REMOVED,
        current_user.id,
        f"Payment method removed: {old_card}",
    )

    return APIResponse(success=True, data={"message": "Payment method removed"})


@router.post("/credits/purchase", response_model=APIResponse[BillingSummaryResponse])
async def purchase_credits(
    data: CreditsPurchase,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Purchase analysis credits (mock implementation)."""
    if not current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No workspace associated with user",
        )

    billing = get_or_create_billing_account(db, current_user.workspace_id)

    if not billing.has_payment_method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please add a payment method first",
        )

    # Mock: Add credits (in production, this would charge the card)
    billing.credits_balance += data.amount
    billing.runs_remaining += data.amount

    db.commit()
    db.refresh(billing)

    # Log event
    log_billing_event(
        db,
        billing.id,
        BillingEventType.CREDITS_PURCHASED,
        current_user.id,
        f"Purchased {data.amount} credits",
        {"amount": data.amount, "new_balance": billing.credits_balance},
    )

    can_run, block_reason = billing.can_run_analysis()

    return APIResponse(
        success=True,
        data=BillingSummaryResponse(
            status=billing.status,
            has_payment_method=billing.has_payment_method,
            card_last4=billing.card_last4,
            card_brand=billing.card_brand,
            card_exp_month=billing.card_exp_month,
            card_exp_year=billing.card_exp_year,
            trial_active=billing.trial_active,
            trial_ends_at=billing.trial_ends_at,
            subscription_active=billing.subscription_active,
            subscription_plan=billing.subscription_plan,
            credits_balance=billing.credits_balance,
            runs_remaining=billing.runs_remaining,
            can_run_analysis=can_run,
            block_reason=block_reason,
        )
    )


@router.get("/events", response_model=APIResponse)
async def list_billing_events(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List billing events for audit trail."""
    if not current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No workspace associated with user",
        )

    billing = get_or_create_billing_account(db, current_user.workspace_id)

    events = db.query(BillingEvent).filter(
        BillingEvent.billing_account_id == billing.id
    ).order_by(BillingEvent.created_at.desc()).limit(50).all()

    event_list = []
    for event in events:
        event_list.append({
            "id": str(event.id),
            "event_type": event.event_type.value,
            "description": event.description,
            "metadata": event.event_metadata,
            "created_at": event.created_at.isoformat(),
        })

    return APIResponse(success=True, data=event_list)
