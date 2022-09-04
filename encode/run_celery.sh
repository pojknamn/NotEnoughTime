#!/bin/zsh
alias rd="docker run redis -d -p 6379:6379"
alias flw="celery --broker=redis://localhost:6379 flower --port=5555"
alias wrkr="celery -A encode.celery worker --concurrency=1 --loglevel=info"
alias bt="celery -A encode.celery beat"
$(bt & wrkr & flw &)
