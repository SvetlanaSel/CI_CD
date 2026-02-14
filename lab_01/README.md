# Лабораторная работа №1. Установка и настройка Docker. Работа с контейнерами в Docker. Вариант 13

## Цель работы
Освоить процесс установки и настройки Docker, научиться работать с основными командами CLI, контейнерами и образами. Понять принципы контейнеризации для развертывания аналитических сред и сервисов.

## Ход работы

### Шаг 1. Проверка установки
Проверяем, что Docker установлен корректно:

```bash
docker --version

```
Вывод:

<img width="884" height="79" alt="image" src="https://github.com/user-attachments/assets/c5e41ca5-d9fb-422f-bba3-7c44c6a1fffb" />


Запускаем тестовый контейнер:
```bash
docker run hello-world
# Вы должны увидеть сообщение: "Hello from Docker! This message shows that your installation appears to be working correctly."
```
Вывод:

<img width="800" height="418" alt="image" src="https://github.com/user-attachments/assets/e114a999-667d-4801-b305-6bc0355bd0e8" />


### Шаг 2. Знакомство с командами Docker CLI
Выполняем следующие команды:

1.  Просмотр скачанных образов:
    ```bash
    docker images
    ```
   Вывод:
   
<img width="885" height="235" alt="image" src="https://github.com/user-attachments/assets/7e8e6171-d8c6-4e19-977a-addd7c819688" />

   
