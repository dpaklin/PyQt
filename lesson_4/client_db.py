#from sqlalchemy import *
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

"""Класс, описывающий данные на стороне клиента."""
class ClientStorage:
    Base = declarative_base()

    class Contacts(Base):
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        contact_name = Column(String, unique=True)

        def __init__(self, contact_name):
            self.contact_name = contact_name

    class Posts(Base):
        __tablename__ = 'posts'
        id = Column(Integer, primary_key=True)
        user_from = Column(String)
        user_to = Column(String)
        post = Column(Text)
        created_at = Column(DateTime)

        def __init__(self, user_from, user_to, post):
            self.user_from = user_from
            self.user_to = user_to
            self.post = post
            self.created_at = datetime.now()

    def __init__(self, path: str, client_name: str):
        self.db_engine = create_engine(f'sqlite:///{path}_{client_name}.db3', echo=False, pool_recycle=7200,
                                       connect_args={'check_same_thread': False})
        self.Base.metadata.create_all(self.db_engine)

        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()

    def add_contact(self, contact_name: str):
        """Записывает имя контакта в базу клиента."""
        contact = self.session.query(self.Contacts).filter_by(contact_name=contact_name)
        # Если нет среди контактов:
        if not contact.count():
            new_contact = self.Contacts(contact_name)
            self.session.add(new_contact)
            self.session.commit()

    def remove_contact(self, contact_name: str):
        """Удаляет контакт пользователя."""
        contact = self.session.query(self.Contacts).filter_by(contact_name=contact_name)
        if contact.count():
            contact.delete()
        self.session.commit()

    def get_contacts(self):
        """Возвращает список контактов."""
        response = self.session.query(self.Contacts.contact_name).all()
        contacts = []
        for contact in response:
            contacts.append(contact[0])
        return contacts

    def get_message_history(self, contact_name: str=None):
        """Возвращает историю переписки."""
        response = self.session.query(self.Posts)
        if contact_name:
            response = response.filter(or_(self.Posts.user_from==contact_name, self.Posts.user_to==contact_name))
        messages = []
        for message in response.all():
            messages.append((message.user_from, message.user_to, message.post, message.created_at))
        return messages

    def save_message(self, user_from: str, user_to: str, post: str):
        """Сохраняет в базе историю сообщений."""
        message = self.Posts(user_from, user_to, post)
        self.session.add(message)
        self.session.commit()


if __name__ == '__main__':
    db_path = 'test'
    client_name = 'client1'
    test_db = ClientStorage(db_path, client_name)

    test_db.add_contact('client2')
    test_db.add_contact('client3')
    test_db.add_contact('client4')
    print(test_db.get_contacts())

    test_db.add_contact('client4')
    print(test_db.get_contacts())

    test_db.save_message('client1', 'client2', 'Hi, client2')
    test_db.save_message('client2', 'client1', 'Hello, client1')
    test_db.save_message('client1', 'client3', 'Hi, client3')
    print(test_db.get_message_history())
    print(test_db.get_message_history('client2'))

    test_db.remove_contact('client4')
    print(test_db.get_contacts())