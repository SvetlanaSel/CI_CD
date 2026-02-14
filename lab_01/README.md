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

1. Создание запускающего файла:
   ```bash
    nano start_metabase.sh
    ```
Содержимое файла:
```
#!/bin/bash

docker run -d \
    -p 3000:3000 \
    --name metabase \
    metabase/metabase:latest
```
Вывод:

<img width="1144" height="709" alt="image" src="https://github.com/user-attachments/assets/56865b81-439e-414d-9c5b-12b8c3b07239" />

2. Задаем файлу уровень доступа:

<img width="633" height="32" alt="image" src="https://github.com/user-attachments/assets/dd4aa14e-b5d6-4914-9be7-6c669bd5a8aa" />

3. Запуск файла:

```
./start_metabase.sh
```
Вывод:

<img width="635" height="240" alt="image" src="https://github.com/user-attachments/assets/a5db3814-9ff0-46a3-9529-864a93e2b6a7" />

4. Проверка запущенных контейнеров:
```
    docker ps
```
Вывод:

<img width="838" height="205" alt="image" src="https://github.com/user-attachments/assets/50c86689-8ceb-41c9-b462-95b5732a7374" />

5. Переход к нужному порту (3000):

В браузере перехожу по адресу localhost:3000

Вывод:

<img width="1313" height="827" alt="image" src="https://github.com/user-attachments/assets/99c8c761-c216-416f-b6b9-f08d3724662d" />

Metabase успешно запустился. Прохожу регистрацию:

<img width="1080" height="738" alt="image" src="https://github.com/user-attachments/assets/f4735f01-7791-457a-a426-cc2c3871c48e" />

<img width="1251" height="749" alt="image" src="https://github.com/user-attachments/assets/3757dbcc-4943-451b-aa89-b97c4423b03d" />




