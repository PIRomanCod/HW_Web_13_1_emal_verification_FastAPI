from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    The get_user_by_email function takes in an email and a database session, and returns the user with that email if it exists. If no such user exists, it returns None.

    :param email: str: Filter the query by email
    :param db: Session: Pass the database session to the function
    :return: A user object if the user exists in the database,
    :doc-author: Trelent
    """
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserModel, db: Session):
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Create a new user
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    g = Gravatar(body.email)

    new_user = User(**body.dict(), avatar=g.get_image())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    """
    The update_token function updates the refresh token for a user in the database.
        Args:
            user (User): The User object to update.
            refresh_token (str): The new refresh token to store in the database.
            db (Session): A connection to our Postgres database.

    :param user: User: Pass the user object to the function
    :param refresh_token: Update the user's refresh token in the database
    :param db: Session: Pass the database session to the function
    :return: The user object
    :doc-author: Trelent
    """
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session, and sets the confirmed field of the user with that email to True.

    :param email: str: Specify the email of the user to be confirmed
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: Find the user in the database
    :param url: str: Specify the type of data that is expected to be passed in
    :param db: Session: Pass the database session to the function
    :return: The updated user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_password(user: User, new_password: str, db: Session) -> None:
    """
    The update_password function takes in a user object, a new password string, and the database session.
    It then updates the user's password to be equal to the new_password string.

    :param user: User: Identify the user whose password is being updated
    :param new_password: str: Pass the new password to the function
    :param db: Session: Pass the database session to the function
    :return: None, because it doesn't have a return statement
    :doc-author: Trelent
    """
    user.password = new_password
    db.commit()


async def update_reset_token(user: User, reset_token, db: Session) -> None:
    """
    The update_reset_token function updates the password reset token for a user.

    :param user: User: Identify the user that is requesting a password reset
    :param reset_token: Update the user's password reset token
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user.password_reset_token = reset_token
    db.commit()
