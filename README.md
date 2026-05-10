# Yadro TestTask — Пошаговая автоматизация с Bash/Python, Docker и Ansible

## Структура проекта

```
.
├── sections1/          # Раздел 1: Python скрипт
│   ├── http_checker.py
│   └── requirements.txt
├── sections2/          # Раздел 2: Docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── http_checker.py
│   └── requirements.txt
└── sections3/          # Раздел 3: Ansible
    ├── inventory.ini
    └── playbook.yml
```

---

## Раздел 1: Python скрипт

### Что сделано
Разработан скрипт `http_checker.py`, который выполняет 5 HTTP-запросов и обрабатывает ответы по группам статус-кодов:

| Диапазон | Действие |
|----------|----------|
| 1xx, 2xx, 3xx | Логирует статус-код и тело ответа (`INFO`) |
| 4xx, 5xx | Генерирует `RuntimeError` и логирует его (`ERROR`) |

### Проблемы и решения
- **Сервис `httpstat.us`** — изначально использовался согласно ТЗ, однако при тестировании на виртуальной машине (Ubuntu 24.04, Proxmox) сервис блокировал все входящие запросы с ошибкой `Connection aborted`. Принято решение заменить на `httpbin.org/status` — он выполняет аналогичную функцию и работает стабильно.

### Запуск
```bash
pip install -r requirements.txt
python3 http_checker.py
```

---

## Раздел 2: Docker

### Что сделано
- Написан `Dockerfile` на базе `ubuntu:22.04` согласно требованиям ТЗ
- Устанавливаются зависимости через `apt` и `pip3`
- Скрипт запускается автоматически при старте контейнера
- Настроен `docker-compose.yml` для удобного запуска

### Проблемы и решения
- **Базовый образ** — изначально использовался `python:3.13-slim`, что не соответствовало ТЗ. Исправлено на `ubuntu:22.04`
- **Устаревший параметр `version`** в `docker-compose.yml` — убран, так как вызывал предупреждения в новых версиях Docker Compose

### Запуск
```bash
cd sections2
docker compose up --build
docker logs http_checker
```

---

## Раздел 3: Ansible

### Что сделано
Написан `playbook.yml` с двумя play:

**Play 1 — Установка Docker:**
- Проверяет наличие Docker на хосте
- Если Docker не установлен — устанавливает через apt (зависимости, GPG ключ, репозиторий, docker-ce)
- Добавляет текущего пользователя в группу `docker`
- Включает и запускает `docker.service`
- Выводит версию Docker

**Play 2 — Деплой контейнера:**
- Собирает Docker образ через `docker compose`
- Ожидает завершения работы контейнера
- Выводит логи контейнера через Ansible (доп. задание)

### Проблемы и решения
- **Зависание `gather_facts`** — на WSL+Docker Desktop Ansible зависал на сборе фактов. Решено добавлением `gather_facts: false`
- **Зависание `become: true`** — sudo через Ansible зависал в WSL окружении. Решено настройкой `NOPASSWD` в `/etc/sudoers`
- **`ansible_user_id` не определён** без `gather_facts` — заменено на `lookup('env', 'USER')` для универсальности
- **Тестирование реальной установки Docker** — проводилось на чистой Ubuntu 24.04 VM в Proxmox (IP: 192.168.10.118). Docker был предварительно удалён, после чего playbook успешно установил его с нуля

### Запуск локально
```bash
cd sections3
pip install ansible
ansible-galaxy collection install community.docker
ansible-playbook -i inventory.ini playbook.yml
```

### Запуск на удалённом хосте
Измените `inventory.ini`:
```ini
[local]
<IP_АДРЕС> ansible_user=<ИМЯ_ПОЛЬЗОВАТЕЛЯ> ansible_connection=ssh
```

Затем:
```bash
ansible-playbook -i inventory.ini playbook.yml --ask-become-pass
```