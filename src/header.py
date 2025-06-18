class Token:
    def __init__(self, token: str):
        self.token = token


class BearerToken(Token):
    def __init__(self, token: str):
        super().__init__(token)

    @property
    def header(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}
