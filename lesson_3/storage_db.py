from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

"""Класс, описывающий данные на стороне сервера."""
class Storage:
    class Users(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True)
        password = Column(String)
        last_login = Column(DateTime)
        is_active = Column(Boolean, default=False)

        def __init__(self, username, is_active=False, password=None):
            self.username = username
            self.password = password
            self.last_login = datetime.now()
            self.is_active = is_active

    class Contacts(Base):
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        user = Column(ForeignKey('users.id'))
        contact = Column(ForeignKey('users.id'))

        def __init__(self, user, contact):
            self.user = user
            self.contact = contact

    class History(Base):
        __tablename__ = 'history'
        id = Column(Integer, primary_key=True)
        user = Column(ForeignKey('users.id'))
        login_time = Column(DateTime)
        ip = Column(String)
        port = Column(String)

        def __init__(self, user_id, date, ip, port):
            self.user = user_id
            self.login_time = date
            self.ip = ip
            self.port = port

    def __init__(self, path):
        self.db_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200)
        self.metadata = Base.metadata
        self.metadata.create_all(self.db_engine)

        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()

    def deactivate_users(self):
        """Устанавливает статус всех клиентов неактивным в момент запуска сервера."""
        users = self.session.query(self.Users).all()
        for user in users:
            user.is_active = False
        self.session.commit()

    def toggle_activity(self, user):
        """Изменяет статус активности пользователя."""
        try:
            user.is_active = not user.is_active
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()

    def add_user(self, user_name):
        """Принимает имя клиента и записывает его данные в таблицу Users."""
        some_user = self.Users(user_name)
        self.session.add(some_user)
        self.session.commit()

    def add_history(self, user, ip_address, port):
        """Принимает имя пользователя и его входные параметры и записывает их в таблицу History."""
        history_user = self.History(user.id, datetime.now(), ip_address, port)
        self.session.add(history_user)
        self.session.commit()

    def login_user(self, user_name: str, ip_address: str, port):
        """Фиксирует вход пользователя."""
        # Проверяем, есть ли в списке зарегистрированных
        user = self.session.query(self.Users).filter_by(username=user_name).first()
        # Если пользователь зарегистрирован, обновляем данные
        if user:
            user.last_login = datetime.now()
            self.session.commit()
        # Если нет, создаем нового
        else:
            self.add_user(user_name)
        # Делаем активным
        user = self.session.query(self.Users).filter_by(username=user_name).first()
        self.toggle_activity(user)
        self.add_history(user, ip_address, port)

    def logout_user(self, user_name):
        """Фиксирует выход пользователя."""
        response = self.session.query(self.Users).filter_by(username=user_name)
        user = response.first()
        self.toggle_activity(user)

    def add_contact(self, user_name, contact_name):
        """Добавляет новый контакт пользователя."""
        user = self.session.query(self.Users).filter_by(username=user_name).first()
        contact = self.session.query(self.Users).filter_by(username=contact_name).first()

        # Если нет среди контактов:
        user_contacts = self.session.query(self.Contacts).filter_by(user=user.id, contact=contact.id)
        if not user_contacts.count():
            new_contact = self.Contacts(user.id, contact.id)
            self.session.add(new_contact)
            self.session.commit()

    def remove_contact(self, user_name, contact_name):
        """Удаляет контакт пользователя."""
        user = self.session.query(self.Users).filter_by(username=user_name).first()
        contact = self.session.query(self.Users).filter_by(username=contact_name).first()

        if contact:
            self.session.query(self.Contacts). \
                filter(self.Contacts.user == user.id, self.Contacts.contact == contact.id).delete()
        self.session.commit()


    def get_users_list(self):
        """Возвращает список всех клиентов."""
        response = self.session.query(self.Users.username, self.Users.is_active, self.Users.last_login).all()
        return response

    def get_user_contacts(self, user_name):
        """Возвращает список контактов пользователя."""
        # Выбираем пользователя
        user = self.session.query(self.Users).filter_by(username=user_name).one()
        # Выбираем его контакты
        response = self.session.query(self.Contacts, self.Users.username).filter_by(user=user.id). \
            join(self.Users, self.Contacts.contact == self.Users.id).all()
        contacts = []
        for contact in response:
            contacts.append(contact[1])
        return contacts

    def get_active_users(self):
        """Возвращает список активных пользователей."""
        response = self.session.query(self.Users.username).filter_by(is_active=True).all()
        return response

    def get_history(self, user_name=None):
        """Возвращает историю подключений пользователей."""
        response = self.session.query(self.Users.username, self.History.login_time, self.History.ip, self.History.port). \
            join(self.Users)
        if user_name:
            response = response.filter_by(username=user_name)
        return response.all()


if __name__ == '__main__':
    db_path = 'server_db.db3'

    test_db = Storage(db_path)
    test_db.login_user('client1', '192.168.0.10', '9999')
    test_db.login_user('client2', '192.168.0.20', '7777')
    test_db.logout_user('client1')
    print('active_users: ', test_db.get_active_users())
    test_db.login_user('client1', '192.168.0.40', '9988')
    test_db.login_user('client3', '192.168.0.30', '5555')

    test_db.add_contact('client1', 'client2')
    test_db.add_contact('client2', 'client3')
    test_db.add_contact('client1', 'client3')

    print('users_list: ', test_db.get_users_list())
    print('active_users: ', test_db.get_active_users())
    print('user_contacts: ', test_db.get_user_contacts('client1'))
    print('history: ', test_db.get_history('client1'))

    test_db.remove_contact('client1', 'client2')
    print('user_contacts: ', test_db.get_user_contacts('client1'))