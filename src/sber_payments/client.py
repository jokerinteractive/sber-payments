import logging
import requests

from .exceptions import ApiError, BadCredentialsException


class Client(object):
    """Performs requests to the SBER API."""

    URL = 'https://3dsec.sberbank.ru/payment/rest/'

    def __init__(self, username: str = None, password: str = None, token: str = None):
        """
        :param username: SBER API username
        :param password: SBER API password
        """

        if username and password:
            self.username = username
            self.password = password
            self.params = {
                'userName': self.username,
                'password': self.password,
            }
        elif token:
            self.token = token
            self.params = {
                'token': self.token,
            }
        else:
            raise BadCredentialsException('Авторизация через логин/пароль или токен, выберите что-то одно')

        self.default_headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
        }
        self.logger = logging.getLogger('sber')

    def _get(self, url: str, params: dict = None):
        resp = requests.get(url, headers=self.default_headers, params=params)
        if not resp.ok:
            raise ApiError(resp.status_code, resp.text)
        return resp.json()

    def _post(self, url: str, params: dict = None):
        resp = requests.post(url, headers=self.default_headers, params=params)
        if not resp.ok:
            raise ApiError(resp.status_code, resp.text)
        return resp.json()

    def register_order(self, order_number: str, amount: int, return_url: str, **kwargs: dict):
        """
        Запрос регистрации заказа (register.do)
        https://securepayments.sberbank.ru/wiki/doku.php/integration:api:rest:requests:register

        :param order_number: Номер (идентификатор) заказа в системе магазина, уникален
                             для каждого магазина в пределах системы. Если номер заказа
                             генерируется на стороне платёжного шлюза, этот параметр
                             передавать необязательно.
        :param amount: Сумма возврата в минимальных единицах валюты.
        :param return_url: Адрес, на который требуется перенаправить пользователя в
                           случае успешной оплаты. Адрес должен быть указан полностью,
                           включая используемый протокол.
        :param kwargs: Необязательные данные.
        """
        url = f"{self.URL}register.do"
        params = {
            'orderNumber': order_number,
            'amount': amount,
            'returnUrl': return_url
        }
        # py3.9: self.params |= params

        return self._post(url, params={**self.params, **params})

    def register_order_pre_auth(self, order_number: str, amount: str, return_url: str, **kwargs: dict):
        """
        Запрос регистрации заказа с предавторизацией (registerPreAuth.do)
        https://securepayments.sberbank.ru/wiki/doku.php/integration:api:rest:requests:registerpreauth

        :param order_number: Номер (идентификатор) заказа в системе магазина, уникален
                             для каждого магазина в пределах системы. Если номер заказа
                             генерируется на стороне платёжного шлюза, этот параметр
                             передавать необязательно.
        :param amount: Сумма возврата в минимальных единицах валюты.
        :param return_url: Адрес, на который требуется перенаправить пользователя в
                           случае успешной оплаты. Адрес должен быть указан полностью,
                           включая используемый протокол.
        :param kwargs: Необязательные данные.
        """
        url = f"{self.URL}registerPreAuth.do"
        params = {
            'orderNumber': order_number,
            'amount': amount,
            'returnUrl': return_url
        }
        if kwargs.get('description'):
            params['description'] = kwargs.get('description')
        # py3.9: self.params |= params

        return self._post(url, params={**self.params, **params})
