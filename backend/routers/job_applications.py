from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import timezone

from database import get_db, SessionLocal
from models import User, MasterProfile, JobApplication, Order, Subscription
from schemas import JobApplicationCreate, JobApplicationResponse, JobApplicationStatusUpdate, MessageResponse
from routers.auth import get_current_user_from_header
from notification_manager import notification_manager
from routers.orders import complete_order_after_delay
from utils.security import mask_phone, filter_description
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/job-applications", tags=["Job Applications"])


@router.post("/{master_id}", response_model=JobApplicationResponse)
async def create_job_application(
    master_id: int,
    data: JobApplicationCreate,
    background_tasks: BackgroundTasks,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """
    Employer submits a job application to a specific master.
    The master receives a notification about the new application.
    """
    user = get_current_user_from_header(authorization, db)
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Ваш профиль заблокирован")

    # Find master profile
    profile = db.query(MasterProfile).options(
        joinedload(MasterProfile.user)
    ).filter(MasterProfile.id == master_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Мастер не найден")

    # Don't allow applying to yourself
    if profile.user_id == user.id:
        raise HTTPException(status_code=400, detail="Нельзя оставить заявку себе")

    # Create application
    application = JobApplication(
        employer_id=user.id,
        master_id=master_id,
        description=data.description,
        city=data.city,
        phone=data.phone or user.phone,
        status="pending"
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    # Send notification to master
    background_tasks.add_task(
        notification_manager.send_notification,
        profile.user_id, "job_application",
        {
            "application_id": application.id,
            "employer_name": user.name,
            "employer_id": user.id,
            "description": data.description,
            "city": data.city,
            "phone": data.phone or user.phone,
        }
    )

    return JobApplicationResponse(
        id=application.id,
        employer_id=user.id,
        employer_name=user.name,
        employer_phone=data.phone or user.phone,
        employer_avatar=user.avatar,
        master_id=master_id,
        master_name=profile.user.name,
        description=application.description,
        city=application.city,
        phone=application.phone,
        status=application.status,
        created_at=application.created_at,
    )


@router.get("/my/sent", response_model=List[JobApplicationResponse])
def get_my_sent_applications(
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """Get all applications sent by the current user (employer view)."""
    user = get_current_user_from_header(authorization, db)
    
    apps = db.query(JobApplication).options(
        joinedload(JobApplication.employer),
        joinedload(JobApplication.master).joinedload(MasterProfile.user)
    ).filter(
        JobApplication.employer_id == user.id
    ).order_by(JobApplication.created_at.desc()).all()

    result = []
    for app in apps:
        created_at = app.created_at
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        result.append(JobApplicationResponse(
            id=app.id,
            employer_id=app.employer_id,
            employer_name=app.employer.name,
            employer_phone=app.phone,
            employer_avatar=app.employer.avatar,
            master_id=app.master_id,
            master_name=app.master.user.name,
            description=app.description,
            city=app.city,
            phone=app.phone,
            status=app.status,
            created_at=created_at,
        ))
    return result


@router.get("/my/received", response_model=List[JobApplicationResponse])
def get_my_received_applications(
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """Get all applications received by the current master."""
    user = get_current_user_from_header(authorization, db)
    profile = db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=403, detail="Профиль мастера не найден")

    # Check subscription
    from routers.orders import can_accept_orders
    is_subscribed = can_accept_orders(user.id, "master", db)

    apps = db.query(JobApplication).options(
        joinedload(JobApplication.employer),
        joinedload(JobApplication.master).joinedload(MasterProfile.user)
    ).filter(
        JobApplication.master_id == profile.id
    ).order_by(JobApplication.created_at.desc()).all()

    result = []
    for app in apps:
        created_at = app.created_at
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
            
        employer_phone = app.employer.phone
        app_phone = app.phone
        desc = app.description
        if not is_subscribed:
            employer_phone = mask_phone(employer_phone or "")
            app_phone = mask_phone(app_phone or "")
            desc = filter_description(desc or "")
            
        result.append(JobApplicationResponse(
            id=app.id,
            employer_id=app.employer_id,
            employer_name=app.employer.name,
            employer_phone=employer_phone,
            employer_avatar=app.employer.avatar,
            master_id=app.master_id,
            master_name=app.master.user.name,
            description=desc,
            city=app.city,
            phone=app_phone,
            status=app.status,
            created_at=created_at,
        ))
    return result


@router.put("/{application_id}/status", response_model=MessageResponse)
async def update_application_status(
    application_id: int,
    data: JobApplicationStatusUpdate,
    background_tasks: BackgroundTasks,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """Master updates the status of a job application."""
    user = get_current_user_from_header(authorization, db)
    profile = db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=403, detail="Профиль мастера не найден")

    app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if app.master_id != profile.id:
        raise HTTPException(status_code=403, detail="Эта заявка не для вас")

    if data.status not in ("viewed", "accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Неверный статус")

    # Check subscription ONLY for accepting
    if data.status == "accepted":
        from routers.orders import can_accept_orders
        if not can_accept_orders(user.id, "master", db):
            raise HTTPException(status_code=403, detail="Лимит заявок исчерпан или нет подписки. Обновите подписку.")

        sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        if sub:
            sub.ads_used += 1


    app.status = data.status
    
    # If accepted, create a real Order to enable chat and tracking
    if data.status == "accepted":
        # Check if an order already exists for this application to prevent duplicates
        # (Though status update is usually one-way)
        
        new_order = Order(
            client_id=app.employer_id,
            master_id=app.master_id,
            subcategory_id=profile.subcategory_id,
            description=app.description,
            city=app.city or profile.city,
            status="accepted"
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        logger.info(f"Created Order {new_order.id} from JobApplication {app.id}")
        
        # Trigger auto-completion background task for consistency
        background_tasks.add_task(complete_order_after_delay, new_order.id)

    db.commit()

    # Notify employer about status change
    status_text_ru = {"viewed": "просмотрена", "accepted": "принята", "rejected": "отклонена"}
    status_text_uz = {"viewed": "ko'rildi", "accepted": "qabul qilindi", "rejected": "rad etildi"}

    background_tasks.add_task(
        notification_manager.send_notification,
        app.employer_id, "job_application_status",
        {
            "application_id": app.id,
            "master_name": user.name,
            "status": data.status,
            "status_text_ru": status_text_ru.get(data.status, data.status),
            "status_text_uz": status_text_uz.get(data.status, data.status),
        }
    )

    return MessageResponse(message=f"Статус заявки обновлен на: {data.status}")
    

@router.delete("/{application_id}", response_model=MessageResponse)
async def withdraw_job_application(
    application_id: int,
    background_tasks: BackgroundTasks,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """Employer withdraws a job application if it's still pending."""
    user = get_current_user_from_header(authorization, db)
    
    app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
        
    if app.employer_id != user.id:
        raise HTTPException(status_code=403, detail="Вы не можете отменить чужую заявку")
        
    if app.status == "accepted":
        raise HTTPException(status_code=400, detail="Заявка уже принята и перешла в статус заказа. Отмените заказ, если необходимо.")
        
    master_user_id = app.master.user_id
    db.delete(app)
    db.commit()
    
    # Notify master about withdrawal
    background_tasks.add_task(
        notification_manager.send_notification,
        master_user_id, "job_application_withdrawn",
        {
            "employer_name": user.name,
        }
    )
    
    return MessageResponse(message="Заявка успешно отозвана")


