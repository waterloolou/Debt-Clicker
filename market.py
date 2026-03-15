class StockMarket:

    def __init__(self):
        self.stocks = {}
        self.money  = 0

    def create_stock(self, name, price, category="Custom"):
        self.stocks[name] = {
            "price":        price,
            "shares":       0,
            "history":      [price],
            "category":     category,
            "returns":      [],
            "return_index": 0,
        }
        return f"{name} created at ${round(price, 2)}"

    def buy_stock(self, name, shares):
        if name not in self.stocks:
            return "Stock does not exist"
        cost = self.stocks[name]["price"] * shares
        if self.money >= cost:
            self.money -= cost
            self.stocks[name]["shares"] += shares
            return f"Bought {shares} share(s) of {name}"
        return "Not enough money"

    def sell_stock(self, name, shares):
        if name not in self.stocks:
            return "Stock does not exist"
        if self.stocks[name]["shares"] >= shares:
            value = self.stocks[name]["price"] * shares
            self.money += value
            self.stocks[name]["shares"] -= shares
            return f"Sold {shares} share(s) of {name}"
        return "Not enough shares"
