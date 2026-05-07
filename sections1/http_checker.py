#!/usr/bin/env python3
"""
http_checker.py — выполняет HTTP-запросы к https://httpstat.us
и обрабатывает ответы по группам статус-кодов.

Использование:
    python3 http_checker.py
"""

import logging
import sys

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
TEST_CODES = [200, 301, 404, 500, 102]

BASE_URL = "https://httpbin.org/status"

REQUEST_TIMEOUT = 10



def make_request(status_code: int) -> requests.Response:
    url = f"{BASE_URL}/{status_code}"
    logger.info("→ Запрос: GET %s", url)
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers, allow_redirects=True)
    return response


def handle_response(response: requests.Response) -> None:
    """
    Обрабатывает ответ по группам:
      1xx, 2xx, 3xx → логируем содержимое
      4xx, 5xx      → бросаем исключение
    """
    code = response.status_code
    body = response.text.strip()

    if 100 <= code <= 399:
        logger.info(
            "[%d] Успешно | Тело ответа: %s",
            code,
            body if body else "<пусто>",
        )
    elif 400 <= code <= 599:
        raise RuntimeError(
            f"HTTP-ошибка {code}: {body if body else '<нет тела>'}"
        )
    else:
        logger.warning("Неизвестная группа статус-кода: %d", code)


def run(codes: list[int]) -> None:
    """Запускает обработку для каждого кода из списка."""
    logger.info("════════════════════════════════════════")
    logger.info("Начало проверки %d запросов", len(codes))
    logger.info("════════════════════════════════════════")

    for code in codes:
        logger.info("──────────────────────────────────────")
        try:
            response = make_request(code)
            handle_response(response)
        except RuntimeError as exc:
            logger.error("Исключение: %s", exc)
        except requests.exceptions.RequestException as exc:
            logger.error("Ошибка сети при запросе %d: %s", code, exc)

    logger.info("════════════════════════════════════════")
    logger.info("Проверка завершена")
    logger.info("════════════════════════════════════════")


if __name__ == "__main__":
    run(TEST_CODES)