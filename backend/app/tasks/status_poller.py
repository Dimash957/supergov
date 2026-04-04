from app.tasks.celery_app import celery_app

@celery_app.task
def poll_statuses():
    print("Polling external eGov statuses for all active applications...")
    pass

@celery_app.task
def calc_all():
    print("Recalculating benefits matrix for all citizens...")
    pass

@celery_app.task
def calc_agency_scores():
    print("Recalculating composite scores for all agencies...")
    pass
