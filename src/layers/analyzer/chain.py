from typing import List

from pydantic import BaseModel
from lib.token import TokenExchange, Token


class InvalidChain(Exception):
    pass


class ExchangeChain(BaseModel):
    cells: List[TokenExchange] = []

    def __iter__(self):
        return self.cells.__iter__()

    def __str__(self):
        return f"""ExchangeChain(cells={[
            f'{token_exchange.input.exchange} - {token_exchange.input.symbol.name} -> ' 
            f'{token_exchange.output.exchange} - {token_exchange.output.symbol.name}' 
            for token_exchange in self.cells]})"""

    def __repr__(self):
        return self.__str__()

    def __cmp__(self, other):
        return self.cells == other.cells

    def _get_last_cell(self) -> TokenExchange:
        if len(self.cells) == 0:
            raise IndexError("There are no cells")
        return self.cells[len(self.cells) - 1]

    def validate_chain(self):
        if len(self.cells) < 2:
            raise InvalidChain("Chain length is less than 2")

        previous_cell = self.cells[0]
        for i in range(1, len(self.cells)):
            current_cell = self.cells[i]
            if not previous_cell.output.can_convert_to(current_cell.input):
                raise InvalidChain("The previous output token is not the same as the new input token")
            previous_cell = current_cell

        if not self.cells[0].input.can_convert_to(self._get_last_cell().output):
            raise InvalidChain("The chain input is not the same chain output")

    def add_cell(self, cell: TokenExchange):
        if self.cells:
            if not self._get_last_cell().output.can_convert_to(cell.input):
                raise InvalidChain("The previous output token is not the same as the new input token")
        self.cells.append(cell)

    def get_profit_percent(self) -> float:
        self.validate_chain()

        if len(self.cells) == 0:
            return 0

        first_exchange = self.cells[0]

        current_token = Token(**first_exchange.input.dict())
        for cell in self.cells:
            price = current_token.price * cell.input.price / cell.output.price
            current_token = Token(price=price, symbol=cell.output.symbol, exchange=cell.output.exchange)

        return 1 - (first_exchange.input.price / current_token.price)
