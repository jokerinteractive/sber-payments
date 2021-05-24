import logging
import requests

from .exceptions import ApiError, BadCredentialsException


class Client(object):
    """Performs requests to the SBER API."""

    URL = 'https://3dsec.sberbank.ru/payment/rest/'

    def __init__(self, username: str = None, password: str = None, token: str = None):
        """
        :param username: Логин служебной учётной записи продавца. При передаче логина и пароля для аутентификации в
                         платёжном шлюзе параметр token передавать не нужно.
        :param password: Пароль служебной учётной записи продавца. При передаче логина и пароля для аутентификации в
                         платёжном шлюзе параметр token передавать не нужно.
        :param token: Значение, которое используется для аутентификации продавца при отправке запросов в платёжный шлюз.
                      При передаче этого параметра параметры userName и password передавать не нужно.
                      Чтобы получить открытый ключ, обратитесь в техническую поддержку.
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
        :param amount: Сумма возврата в минимальных единицах валюты (в копейках или центах).
        :param return_url: Адрес, на который требуется перенаправить пользователя в
                           случае успешной оплаты. Адрес должен быть указан полностью,
                           включая используемый протокол.
        :param kwargs: Необязательные данные.
        """
        url = f"{self.URL}register.do"
        params = {
            'orderNumber': order_number,
            'amount': amount,
            'returnUrl': return_url,
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
        :param amount: Сумма возврата в минимальных единицах валюты (в копейках или центах).
        :param return_url: Адрес, на который требуется перенаправить пользователя в
                           случае успешной оплаты. Адрес должен быть указан полностью,
                           включая используемый протокол.
        :param kwargs: Необязательные данные.
        """
        url = f"{self.URL}registerPreAuth.do"
        params = {
            'orderNumber': order_number,
            'amount': amount,
            'returnUrl': return_url,
        }
        if kwargs.get('description'):
            params['description'] = kwargs.get('description')
        # py3.9: self.params |= params

        return self._post(url, params={**self.params, **params})

    def deposit(self, order_id: str, amount: int = 0):
        """
        Запрос завершения на полную сумму в деньгах (deposit.do)
        https://securepayments.sberbank.ru/wiki/doku.php/integration:api:rest:requests:deposit

        Для запроса завершения ранее пред авторизованного заказа используется запрос deposit.do.

        :param order_id: Номер заказа в платежной системе. Уникален в пределах системы. Отсутствует если регистрация
                         заказа на удалась по причине ошибки, детализированной в ErrorCode.
        :param amount: Сумма возврата в минимальных единицах валюты (в копейках или центах).
                       Внимание! Если в этом параметре указать 0, завершение произойдёт на всю предавторизованную сумму.
        """
        url = f"{self.URL}deposit.do"
        params = {
            'orderId': order_id,
            'amount': amount,
        }
        return self._post(url, params={**self.params, **params})

    def reverse(self, order_id: str, amount: int = None, **kwargs: dict):
        """
        Запрос отмены оплаты заказа (reverse.do)
        https://securepayments.sberbank.ru/wiki/doku.php/integration:api:rest:requests:reverse

        Для запроса отмены оплаты заказа используется запрос reverse.do. Функция отмены доступна в течение ограниченного
        времени после оплаты, точные сроки необходимо уточнять в «Сбербанке». Нельзя проводить отмены и возвраты
        по заказам, инициализирующим регулярные платежи, т. к. в этих случаях не происходит реального списания денег.

        Операция отмены оплаты может быть совершена только один раз. Если она закончится ошибкой, то повторная операция
        отмены платежа не пройдёт. Эта функция доступна магазинам по согласованию с банком. Для выполнения операции
        отмены продавец должен обладать соответствующими правами.

        При проведении частичной отмены (отмены части оплаты) сумма частичной отмены передается в необязательном
        параметре amount. Частичная отмена возможна при наличии у магазина соответствующего разрешения в системе.
        Частичная отмена невозможна для заказов с фискализацией, корзиной и лоялти.

        :param order_id: Номер заказа в платежной системе. Уникален в пределах системы. Отсутствует если регистрация
                         заказа на удалась по причине ошибки, детализированной в ErrorCode.
        :param amount: Сумма частичной отмены. Параметр, обязательный для частичной отмены.
        """
        url = f"{self.URL}reverse.do"
        params = {
            'orderId': order_id,
            'amount': amount,
        }
        return self._post(url, params={**self.params, **params})

    def refund(self, order_id: str, amount: int = 0):
        """
        Запрос возврата на полную сумму в деньгах (refund.do)
        https://securepayments.sberbank.ru/wiki/doku.php/integration:api:rest:requests:refund

        По этому запросу средства по указанному заказу будут возвращены плательщику. Запрос закончится ошибкой в случае,
        если средства по этому заказу не были списаны. Система позволяет возвращать средства более одного раза,
        но в общей сложности не более первоначальной суммы списания.

        Для выполнения операции возврата необходимо наличие соответствующих права в системе.

        :param order_id: Номер заказа в платежной системе. Уникален в пределах системы. Отсутствует если регистрация
                         заказа на удалась по причине ошибки, детализированной в ErrorCode.
        :param amount: Сумма возврата в минимальных единицах валюты (в копейках или центах).
                       Внимание! Если в запросе указать amount=0, производится возврат на всю сумму заказа.
        """
        url = f"{self.URL}refund.do"
        params = {
            'orderId': order_id,
            'amount': amount,
        }
        return self._post(url, params={**self.params, **params})

    def get_order_status(self, order_id: str):
        """
        Расширенный запрос состояния заказа
        https://securepayments.sberbank.ru/wiki/doku.php/integration:api:rest:requests:getorderstatusextended

        :param order_id: Номер заказа в платежной системе. Уникален в пределах системы. Отсутствует если регистрация
                         заказа на удалась по причине ошибки, детализированной в ErrorCode.
        """
        url = f"{self.URL}getOrderStatusExtended.do"
        params = {
            'orderId': order_id,
        }
        return self._post(url, params={**self.params, **params})
