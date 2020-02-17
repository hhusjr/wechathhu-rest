celery worker -A wechathhu -l debug -Q multi &
celery worker -A wechathhu -l debug -Q single -c 1 &
