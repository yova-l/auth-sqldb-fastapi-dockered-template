from pydantic import BaseModel

class PersonalizedWriteRequest(BaseModel):
    msg: str

class MyProcessor(BaseModel):
    message: str = "Process completed: "

    def process(self, message: str, pageid: str, username: str) -> str:
        return f"{self.message} '{message}' correctly processed on page: '{pageid}'. All necessary services were used. Bye {username}!"

