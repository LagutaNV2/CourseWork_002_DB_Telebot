import configparser

import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, session

Base = declarative_base()


class Known_users(Base):
    __tablename__ = "known_users"
    id = sq.Column(sq.Integer, primary_key=True)
    cid = sq.Column(sq.String(length=40), unique=True)

    def __str__(self):
        return f'user: {self.id}: {self.cid}'


class Dictionary(Base):
    __tablename__ = "dictionary"
    id = sq.Column(sq.Integer, primary_key=True)
    target_word = sq.Column(sq.String(length=55), unique=True)
    translate_word = sq.Column(sq.String(length=55), unique=True)
    user_step = sq.Column(sq.Integer, nullable=False)

    def __str__(self):
        return f'word: {self.id}: ({self.target_word}, {self.translate_word })'


class Users_dict(Base):
    __tablename__ = "users_dict"
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("known_users.id"), nullable=False)
    dict_id = sq.Column(sq.Integer, sq.ForeignKey("dictionary.id"), nullable=False)

    known_users = relationship(Known_users, backref="users_dicts")
    dictionary = relationship(Dictionary, backref="users_dicts")

    def __str__(self):
        return f'personal_dict: {self.id}: (user_id - {self. user_id }, dict_id - {self. dict_id }, step - {self. user_step})'


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    word01 = Dictionary(target_word='Peace', translate_word='Мир', user_step=0)
    word02 = Dictionary(target_word='Green', translate_word='Зеленый', user_step=0)
    word03 = Dictionary(target_word='White', translate_word='Белый', user_step=0)
    word04 = Dictionary(target_word='Exception', translate_word='Исключение', user_step=0)
    word05 = Dictionary(target_word='Source', translate_word='Источник', user_step=0)
    word06 = Dictionary(target_word='Error', translate_word='Ошибка', user_step=0)
    word07 = Dictionary(target_word='Coroutine', translate_word='Сопрограмма', user_step=0)
    word08 = Dictionary(target_word='Debugger', translate_word='Отладчик', user_step=0)
    word09 = Dictionary(target_word='Sending', translate_word='Отправка', user_step=0)
    word10 = Dictionary(target_word='Solving', translate_word='Решение', user_step=0)
    word11 = Dictionary(target_word='Checking', translate_word='Проверка', user_step=0)

    session.add_all([word01, word02, word03, word04, word05, word06, word07, word08, word09, word10, word11])
    session.commit()


def start_session_postgres():
    config = configparser.ConfigParser()
    config.read('setting.ini')
    DSN = config["PSQL"]["DSN"]
    # engine = sq.create_engine(DSN, echo=True, pool_pre_ping=True)
    engine = sq.create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    return engine, session

if __name__ == '__main__':
    # создание БД и заполнение словаря первоначальным набором слов
    engine, session = start_session_postgres()
    create_tables(engine)
    session.close()

