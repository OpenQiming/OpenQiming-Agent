import datetime
import logging
import time

import click
from werkzeug.exceptions import NotFound

from agent_platform_basic.extensions.ext_database import db
from agent_platform_core.indexing_runner import DocumentIsPausedException, IndexingRunner
from agent_platform_core.models.db_model.dataset import Document
from agent_platform_service.events.document_index_event import document_index_created


@document_index_created.connect
def handle(sender, **kwargs):
    dataset_id = sender
    document_ids = kwargs.get('document_ids', None)
    documents = []
    start_at = time.perf_counter()
    for document_id in document_ids:
        logging.info(click.style('Start process document: {}'.format(document_id), fg='green'))

        document = db.session.query(Document).filter(
            Document.id == document_id,
            Document.dataset_id == dataset_id
        ).first()

        if not document:
            raise NotFound('Document not found')

        document.indexing_status = 'parsing'
        document.processing_started_at = datetime.datetime.now().replace(tzinfo=None)
        documents.append(document)
        db.session.add(document)
    db.session.commit()

    try:
        indexing_runner = IndexingRunner()
        indexing_runner.run(documents)
        end_at = time.perf_counter()
        logging.info(click.style('Processed dataset: {} latency: {}'.format(dataset_id, end_at - start_at), fg='green'))
    except DocumentIsPausedException as ex:
        logging.info(click.style(str(ex), fg='yellow'))
    except Exception:
        pass
