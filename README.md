# BonchMafia

Этот бот предназначен для рейтинговой фиксации результатов игроков клуба в виде карт пользователей:

![BonchMafia](pictures/logo.png)

1. **Создание рейтинговых карт:** Бот позволяет создавать рейтинговые карты игроков, которые могут включать в себя информацию о роли игрока, его статистике и достижениях в предыдущих играх.

2. **Просмотр карт других игроков:** Игроки могут просматривать карты других участников клуба, чтобы получить информацию о стиле игры, рейтинге и о самых сильных картах.

3. **Регистрация игр:** Бот предоставляет базовый функционал для регистрации игр. Администраторы ведут протоколы игр, которые потом можно занести в бота.

## Требования

Для успешного развертывания и использования BonchMafia Телеграм-бота, вам понадобятся:

- **Учетная запись Телеграм-бота**: Создайте бота через [@BotFather](https://core.telegram.org/bots#botfather) и получите токен для доступа к API.

- **Docker**: Для хранения данных о рейтинговых картах и играх бот использует MongoDB. Убедитесь, что у вас есть аккаунт и данные для подключения к базе данных.

## Установка и настройка

```
git clone https://github.com/hiimluck3r/BonchMafia.git
```

Затем отредактируйте данные в docker-compose.yml (сделайте .env или впишите напрямую, как вам удобнее)

```
version: '3.9'
services:
  db:
    container_name: db
    image: luck3rinc/bonchmafia_db:latest
    restart: always
    environment:
      POSTGRES_USER: $USER
      POSTGRES_PASSWORD: $PASSWORD
      POSTGRES_DB: $DB
    ports:
      - "5432:5432"
    volumes:
      - ./postgresql:/docker-entrypoint-initdb.d
      - ./postgresql/data:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin4_container
    image: dpage/pgadmin4
    restart: always
    environment:
      PGADMIN_DEFAULT_EMAIL: $MAIL
      PGADMIN_DEFAULT_PASSWORD: $PASS
    ports:
      - "80:80"

  main:
    container_name: bonchmafia
    image: luck3rinc/bonchmafia:latest
    restart: on-failure
    environment:
      API_TOKEN: $API_TOKEN
      HOST: $HOST
      DB: $DB
      USER: $USER
      PASSWORD: $PASSWORD
      ADMIN: $ADMIN
      PORT: $PORT
    volumes:
      - ./logs:/~/BonchMafia/logs
      - ./bot/pictures:/~/BonchMafia/bot/pictures
    depends_on:
      - db

volumes:
  logs:
```

После запустите при помощи:
```
docker-compose -p bonchmafia up -d
```

## Лицензия

Этот проект распространяется под лицензией [MIT](LICENSE). Вы можете свободно использовать, изменять и распространять этот код в соответствии с условиями лицензии.