***
P.S. "На стадии Alpha версии нужно учитывать что все компоненты 
могут быть заменены либо убранны. Нет никакой гарантии что 
их конечная задача и надабность будет определена окончательно,
как минимум на этой стадии."

Все компоненты будут покрыты всеми возможными тестами и вообще 
сама разработка будет по TDD, т.к. здесь деньги и одна ошибка 
может стать фатальной.

***
## Поверхностное деление системы на компоненты

- (tracker) Первый и самый очевидный компонент, это компонент мониторинга.
Этот компонент ищет все предложения на каждой бирже, в 
особенности самые выгодные, и сохраняет их в связующее звено. 

- (analizer) Второй компонент это аналитика. Он достаёт предложения из 
связующего звена и анализирует их на возможность получения 
прибыли, если такова имеется, он комуницирует третий компонент 
и даёт информацию о возможности получения прибыли. 

- Третий компонент это компонент транзакций. Он будет держаться 
под строжайшим контролем и изначально будет реализован лишь в 
качестве заглушки. Он будет заниматься тем чтобы принимать решения
о возможности и надобности покупки полученного предложения. В 
случае если есть возможность покупки и удовлетворяет прибыль,
производится транзакция. ("Возможность", речь идёт о наличии 
нужных счетов, баланса на них, и остальных ограничений) 

#### Технические прослойки 
- Упомянутое раннее связующее звено это Redis. В нём будут 
реализованы механизмы для хранения предложений, передачи их
между компонентами, а так же механизм очередей, для отправки
предложений в третий слой. 
- Также будет тотальное логгирование каждого компонента. 
Развёртка будет в консоль, в файл и в ELK для визуализации.

***


