from app.tasks.celery_app import celery_app

@celery_app.task
def calc_agency_scores():
    print("Recalculating composite scores for all agencies...")
    # Add score aggregation logic here
    pass
