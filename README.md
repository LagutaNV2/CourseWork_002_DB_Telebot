Курсовая работа «ТГ-чат-бот «Обучалка английскому языку» по курсу «Базы данных».

Цель проекта - разработать базу данных Telegram-бота для изучения английского языка.

Требования к программному обеспечению в файле requirements.txt.

Порядок действий.
1. Устанавливается psycopg2: $pip install psycopg2-binary.
2. Создается база данных CoursWork_002: $createdb -U postgres CoursWork_002.
3. Запускается файл создания базы данных models.py по схеме, содержащейся в файле  CoursWork_002_DB.png.
4. В Телеграм запускается бот NetoTranslator_bot.
5. Первая команда после входа в  бот: "/start".
6. При первом входе выдается приветствие и заполняется база данных общим набором слов.
7. Далее бот ведет с пользователем диалог:
    спрашивает перевод слова, предлагая 4 варианта ответа на английском языке в виде кнопок;
    при правильном ответе подтверждает ответ, при неправильном - предлагает попробовать снова;
    предлагает добавлять и удалять слова, формируя персонализированный словарь для каждого пользователя.
