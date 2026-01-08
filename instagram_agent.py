from pydantic import BaseModel

class MenuConfig(BaseModel):
    menu_y: int
    home_x: int
    reels_x: int
    messsages_x: int
    search_x: int
    profile_x: int

class IGGraphState:
    """
    Docstring for IGGraphState

    Lists current actions which when triggered transition to different states
    """
    def __init__(self):
        pass

class IGAgent:
    pass