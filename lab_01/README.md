# Лабораторная работа №1. Установка и настройка Docker. Работа с контейнерами в Docker. Вариант 13

## Цель работы
Освоить процесс установки и настройки Docker, научиться работать с основными командами CLI, контейнерами и образами. Понять принципы контейнеризации для развертывания аналитических сред и сервисов.

## Ход работы

### Шаг 1. Установка Docker

Шаг выполнен заранее, докер установлен.

### Шаг 2. Проверка установки
Проверяем, что Docker установлен корректно:

```bash
docker --version

```
Вывод:

<img width="884" height="79" alt="image" src="https://github.com/user-attachments/assets/c5e41ca5-d9fb-422f-bba3-7c44c6a1fffb" />


Запускаем тестовый контейнер:
```bash
docker run hello-world

```
Вывод:

<img width="800" height="418" alt="image" src="https://github.com/user-attachments/assets/e114a999-667d-4801-b305-6bc0355bd0e8" />


### Шаг 3. Знакомство с командами Docker CLI
Выполняем следующие команды:

1.  Просмотр скачанных образов:
    ```bash
    docker images
    ```
   Вывод:
   
<img width="885" height="235" alt="image" src="https://github.com/user-attachments/assets/7e8e6171-d8c6-4e19-977a-addd7c819688" />

2.  Просмотр запущенных контейнеров:
    ```bash
    docker ps
    ```
Вывод:

<img width="707" height="139" alt="image" src="https://github.com/user-attachments/assets/20ad698a-2e30-4a21-ae59-a3ca2647b843" />


3.  Просмотр всех контейнеров (включая остановленные):
    ```bash
    docker ps -a
    ```
Вывод:

<img width="704" height="283" alt="image" src="https://github.com/user-attachments/assets/d9a14397-f306-4b20-8984-43782d9df1a6" />

### Шаг 4. Пример выполнения задания (Вариант 13 — Metabase)





