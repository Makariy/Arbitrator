## API 

В этом документе будут описаны все точки взаимодействия с разными 
биржами, их лимиты и особенности. 

***

### KuCoin 
#### Docs: https://docs.kucoin.com/
##### Base url: https://api.kucoin.com

Все запросы content_type="application/json"

(https://docs.kucoin.com/#request-rate-limit) <br/>
На KuCoin есть возможность получения бидов как GET запросами,
так и через WebSocket. WebSocket обновляется раз в 100 мс. 

WebSocket - здесь всё замысловато. Сначала идёт POST запрос на 
https://api.kucoin.com/api/v1/bullet-public, и из ответа
вытаскивается token и endpoint. Потом можно пингануть их, понгать не хочу.
Далее есть возможность подписаться на нужный для мониторинга канал. Вся
авторизация и настройка достаточно сложная, так что нужно смотреть доки. 

(https://docs.kucoin.com/#websocket-feed)


Все приватные REST запросы должны содержать следующие HTTP header-ы: <br/>
(https://docs.kucoin.com/#authentication)
 - KC-API-KEY The API key as a string.
 - KC-API-SIGN The base64-encoded signature (see Signing a Message).
 - KC-API-TIMESTAMP A timestamp for your request.
 - KC-API-PASSPHRASE The passphrase you specified when creating the API key.
 - KC-API-KEY-VERSION You can check the version of API key on the page of API Management

#### API endpoints HTTP: 
 - /api/v1/market/orderbook/level2_(20|100) - GET - 
[symbol - str] - получить лучшие биды. Возвращает бид 
и кол-во возможных для покупки токенов. 
(https://docs.kucoin.com/#order-book)

#### API endpoints WebSocket:
 - /spotMarket/level2Depth50 - [symbol - str] - 
(https://docs.kucoin.com/#level2-50-best-ask-bid-orders)
получить лучшие биды. Возвращает бид и кол-во возможных для 
покупки токенов. 

***

### Huobi

##### Base url: https://api.huobi.pro
##### Base WebSocket: wss://api.huobi.pro/ws/v2


Лимитировано 50 запросов в секунду на WebSocket

#### API endpoints HTTP:
 - /market/detail/merged?symbol

#### API endpoints WebSocket:
 - market.$symbol.bbo - 
(https://huobiapi.github.io/docs/spot/v1/en/#best-bid-offer)



### GARANTEX 
Во первых, на этой бирже есть API для P2P

### ByBit
(https://bybit-exchange.github.io/docs/futuresV2/linear/#t-websocketauthentication)
Запутанная параша, ничего не понятно, документация говно 

Сначала аутентификация. Для этого есть два метода: 
 - По url прокинуть ключ и подпись. Чтобы получить подпись надо как то 
магически её сделать HMAC-ом  



