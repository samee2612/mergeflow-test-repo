def process_payment(amount, retries=3):

    attempt = 1

    while attempt < retries:
        try:
            return charge_card(amount)
        except Exception:
            attempt += 1

    raise Exception("Payment failed")