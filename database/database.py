from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, File, Page

# TODO scan files and pages for deleted and remove records from database


class DataBase:
    def __init__(self, database_path=None):
        if database_path is not None:
            engine = create_engine(database_path, echo=False)
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            Session.configure(bind=engine)
            self._session = Session

    def _add(self, data):
        session = self._session()
        session.add(data)
        session.commit()
        session.close()

    def add_user(self, name, password):
        user = User(name=name, password=password)
        self._add(user)

    def add_file(self, name, author_id, path):
        file = File(author_id=author_id, name=name, path=path)
        self._add(file)

    def add_page(self, origin_id, name, path):
        page = Page(origin_id=origin_id, name=name, path=path)
        self._add(page)

    def get_user(self, name):
        session = self._session()
        result = session.query(User).filter(User.name == name).first()
        session.close()
        return result

    def get_file(self, name):
        session = self._session()
        result = session.query(File).filter(
            File.name.like('{}%'.format(name))).all()
        session.close()
        return result

    def get_pages(self, origin_id):
        session = self._session()
        result = session.query(Page).filter(Page.origin_id == origin_id).all()
        session.close()
        return result

    def delete_user(self, name):
        session = self._session()
        session.query(User).filter(User.name == name).delete()
        session.commit()
        session.close()
