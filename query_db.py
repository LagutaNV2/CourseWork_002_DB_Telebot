import configparser
import random

import sqlalchemy
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, session
from models import Known_users, Dictionary, Users_dict, start_session_postgres

def get_users(current_cid):
    '''выводит id, cid для знакомого пользователя или None для нового'''
    engine, session = start_session_postgres()
    selected = session.query(Known_users.id, Known_users.cid)\
        .filter(Known_users.cid==str(current_cid)).scalar()
    session.close()
    print('result check_user: ', selected)
    return selected


def add_user(current_cid):
    '''добавление в базу пользователей нового user'''
    engine, session = start_session_postgres()
    user = Known_users(cid=current_cid)
    session.add_all([user])
    session.commit()
    session.close()
    print('added user: cid', current_cid)


def add_users_dict(current_cid):
    '''автоматическое заполнение первоначального индивидуального словаря
    базовым набором слов на англйском языке для нового пользователя'''
    engine, session = start_session_postgres()
    select_id_user = session.query(Known_users.id).filter(Known_users.cid==str(current_cid)).all()[0]
    print('для найденного id_user ', select_id_user)
    select_id_dict = session.query(Dictionary.id).filter(Dictionary.user_step==0).all()
    print('персональный словарь', select_id_dict)
    for word_id in select_id_dict:
        element = Users_dict(user_id=select_id_user[0], dict_id=word_id[0])
        session.add_all([element])
        print('added user_dict: ', select_id_user[0], word_id[0])
        session.commit()
    session.close()


def check_word_in_db(translate_word_new):
    '''возвращает None, если translate_word в общем словаре отсутствует'''
    engine, session = start_session_postgres()
    selected = session.query(Dictionary) \
        .with_entities(Dictionary.id, Dictionary.translate_word, Dictionary.target_word) \
        .filter(Dictionary.translate_word == translate_word_new).scalar()
    session.close()
    print('result check_word in bd: ', selected)
    return selected


def check_word_in_personal_dict(cid, t_word):
    '''возвращает None, если translate_word в индивидуальном словаре отсутствует'''
    engine, session = start_session_postgres()
    selected = session.query(Dictionary) \
        .with_entities(Dictionary.id, Dictionary.translate_word, Dictionary.target_word) \
        .join(Users_dict, Users_dict.dict_id == Dictionary.id) \
        .join(Known_users, Known_users.id == Users_dict.user_id) \
        .filter(Dictionary.target_word == t_word)\
        .filter(Known_users.cid == cid).scalar()
    session.close()
    print('result check_word in_personal_dict: ', selected)
    return selected

def check_pk_in_user_dict(user_id, dict_id):
    '''возвращает id индивидуальной связки из персонального словаря (user_id - dict_id) или None'''
    engine, session = start_session_postgres()
    selected = session.query(Dictionary) \
        .with_entities(Dictionary.id, Dictionary.translate_word, Dictionary.target_word) \
        .join(Users_dict, Users_dict.dict_id == Dictionary.id) \
        .join(Known_users, Known_users.id == Users_dict.user_id) \
        .filter(Users_dict.dict_id == dict_id)\
        .filter(Users_dict.user_id == user_id).scalar()
    session.close()
    print('result check_word in_personal_dict: ', selected)
    return selected

def get_personal_dict(current_cid):
    '''получаем возможный набор всех слов для заполнения карточки данного пользователя'''
    engine, session = start_session_postgres()
    select = session.query(Dictionary) \
        .with_entities(Dictionary.id, Dictionary.translate_word, Dictionary.target_word) \
        .join(Users_dict, Users_dict.dict_id == Dictionary.id) \
        .join(Known_users, Known_users.id == Users_dict.user_id) \
        .filter(Known_users.cid == str(current_cid)).all()
    return select

def get_words_from_bd(current_cid):
    ''' выбираем слово для перевода и формируем набор "неправильных" слов '''
    engine, session = start_session_postgres()
    select = get_personal_dict(current_cid)
    print('select_id_user ', select)
    result = random.choice(select)
    target_id, target_word, translate_word = result[0], result[1], result[2]
    others = []
    while len(others) < 4:
        word_for_others = random.choice(select)
        if word_for_others[2] != translate_word and word_for_others[2] not in others:
            others.append(word_for_others[2])

    return target_word, translate_word, others


def delete_word_from_users_dict(cid, t_word):
    '''удаление из персонального словаря связки (user_id - dict_id)'''
    engine, session = start_session_postgres()
    select = session.query(Users_dict) \
        .with_entities(Users_dict.id) \
        .join(Dictionary, Dictionary.id == Users_dict.dict_id) \
        .join(Known_users, Known_users.id == Users_dict.user_id) \
        .filter(Known_users.cid == str(cid))\
        .filter(Dictionary.target_word == t_word).scalar()
    session.commit()
    print('selected for delete id: ', select)

    personal_dict = get_personal_dict(cid)
    if len(personal_dict) > 5:
        session.query(Users_dict).filter(Users_dict.id == select).delete()
        session.commit()
        session.close()
        return('Done')
    else:
        print('осталось 5 слов, удаление блокировано')
        session.close()
        return ('Blocked')


def add_word_to_db(cid, translate_new, t_word_new):
    '''поэтапное добавление слов в общий и индивидуальный словари; добавление игнорируется,
     если уже существует слово в словаре или связка в инд.словаре'''
    engine, session = start_session_postgres()
    answer = check_word_in_db(translate_new)
    print('result of cheking new translate_new', answer)
    if answer is None:
        word = Dictionary(target_word=t_word_new, translate_word=translate_new, user_step=1)
        session.add_all([word])
        session.commit()
    else:
        print('повтор, в словаре уже есть это слово')

    select_id_user = session.query(Known_users.id).filter(Known_users.cid == str(cid)).all()[0]
    print('select_id_user ', select_id_user[0])

    select_id_dict = session.query(Dictionary.id).filter(Dictionary.target_word == t_word_new).all()[0]
    print('select_id_dict', select_id_dict[0])

    answer = check_pk_in_user_dict(select_id_user[0], select_id_dict[0])
    if answer is None:
        element = Users_dict(user_id=select_id_user[0], dict_id=select_id_dict[0])
        session.add_all([element])
        print('added user_dict: ', select_id_user[0], select_id_dict[0])
        session.commit()
    else:
        print('повтор, в индивидуальной настройке словаря уже есть это слово')
    session.close()


