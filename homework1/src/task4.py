# calculate final price after a discount
# works with any numeric type
# will return the price after subtracting its price's discount percent, discount is 0 to 100
def calculate_discount(price, discount):
    # error handling.. since bool is technically an int in python, reject it explicitly
    if isinstance(price, bool) or isinstance(discount, bool):
        raise TypeError("price and discount must be numeric, not bool")
    
    try:
        # price cant be neg
        if price < 0:
            raise ValueError("price cannot be negative")
        # discount parameter health
        if discount < 0 or discount > 100:
            raise ValueError("discount must be between 0 and 100")
        # calculate 
        return price - (price * discount / 100)
    # ducktyping
    except TypeError as error:
        # anything that can't do comparison or arithmetic lands here
        raise TypeError("price and discount must be numeric") from error


if __name__ == "__main__":
    print(calculate_discount(100, 20))
    print(calculate_discount(19.99, 10.5))
    print(calculate_discount(50, 0))