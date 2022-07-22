from flask import current_app
from . import db


def addToIndex(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, content=payload)


def removeFromIndex(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def queryIndex(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    check = current_app.elasticsearch.search(
        index=index,
        body={
            'query': {'multi_match': {'query': query, 'fields': ['*']}},
            'from': (page - 1) * per_page, 'size': per_page
        }
    )
    ids = [int(hit['_id']) for hit in check['hits']['hits']]
    return ids, check['hits']['total']['value']


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = queryIndex(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                addToIndex(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                addToIndex(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                removeFromIndex(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            addToIndex(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
