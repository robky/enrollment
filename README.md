### Описание
Предлагалось реализовать бэкенд для веб-сервиса хранения информации о 
хранимых файлах (не самих файлов, а информации о них: расположение, размер, тип 
файл/папка и т.п.). Подробнее: [Описание задачи](https://github.com/robky/enrollment/blob/master/Task.md).

### Технологии
Python 3.8
Django 3.2.15
Django MPTT 0.13.4
Django Rest Framework 3.13.1
PostgreSQL
Docker


![example branch parameter](https://github.com/robky/enrollment/actions/workflows/enrollment.yml/badge.svg)

### Состав проекта:
На github action написан workflow, который выполнятся после каждого 
запушенного коммита в ветку master:
1. Тест flake8 и собственные django тесты
2. Сборка контейнера из репозитория и отправка его на docker hub

Так как доступа к виртуальной машине без vpn нет (именно к виртуальной 
машине, а не к контейнеру), то следующий шаг делается не в workflow, а 
в ручную при помощи скриптов. 

Первый (основной) deploy.sh скрипт при помощи docker-composer разворачивает проект 
из 3 контейнеров:
1. db - postgres
2. web - django + gunicorn (образ берется из docker hub)
3. nginx - nginx

Второй (дополнительный, выполняется один раз после первого деплоя) tuning.sh делает 
миграции, подключает статику и выполняет команду на создание суперпользователя. 

### Как запустить проект:
Скачать файлы из [папки deploy](https://github.com/robky/enrollment/tree/master/deploy)

Выполнить последовательно 2 скрипта:
```
deploy.sh
tuning.sh
```
