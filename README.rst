Python библиотека к программному интерфейсу (API) СБЕРа
=======================================================

Подключение через программный интерфейс (API) позволяет использовать всю доступную функциональность платёжного шлюза.

Использование
-------------

.. code-block:: python

    from sber_payments import Client

    client = Client('TOKEN')

    client.register_order(order_number='001', amount=100, return_url='https://shopname.ru/')

