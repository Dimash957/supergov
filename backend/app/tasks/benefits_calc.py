from app.tasks.celery_app import celery_app

@celery_app.task
def calc_all():
    print("Recalculating benefits matrix for all citizens...")
    # Add eligibility generation logic here
    pass
