from fastapi import Depends, HTTPException, status, APIRouter, Security, BackgroundTasks, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail, ResetPassword
from src.services.auth import auth_service, auth_password
from src.services.email import send_email

router = APIRouter(prefix="/api/auth", tags=['auth'])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes in a UserModel object, which is validated by pydantic.
        The password is hashed using Argon2 and stored as such.
        A confirmation email is sent to the user's email address.

    :parameter body: UserModel: Get the data from the request body
    :parameter background_tasks: BackgroundTasks: Add a task to the background queue
    :parameter request: Request: Get the base_url of the server
    :parameter db: Session: Get the database session
    :return: A tuple with two values:
    :doc-author: Trelent
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url,
                              payload={"subject": "Confirm your email", "template_name": "email_template.html"})

    return {"message": "Email confirmed"}, new_user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
        It takes the user's email as username and password from the request body, verifies that they are correct, and returns an access token.

    :parameter body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :parameter db: Session: Pass the database session to the function
    :return: A dict with the access_token, refresh_token and token_type
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token, a new refresh_token, and the type of token.
        If the user's current refresh_token does not match what was passed into this function then it will return an error.

    :parameter credentials: HTTPAuthorizationCredentials: Get the token from the header
    :parameter db: Session: Get the database session
    :return: A dictionary with the access_token, refresh_token and token type
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        The function then checks if there is a user with that email in our database, and if not, returns an error message.
        If there is a user with that email in our database, we check whether their account has already been confirmed or not.
        If it has been confirmed already, we return another error message saying so; otherwise we call repository_users' confirmed_email function which sets the 'confirmed' field of that particular User object

    :param token: str: Get the email from the token
    :param db: Session: Get the database session
    :return: A message if the email is already confirmed or if it is confirmed
    :doc-author: Trelent
    """
    email = auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that they can click on to confirm their email address. The function takes in a RequestEmail object, which contains the user's email address. It then checks if there is already a user with that email address in the database, and if so, it sends them an email containing a link for them to confirm their account.

    :parameter body: RequestEmail: Get the email from the request body
    :parameter background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :parameter request: Request: Get the base_url of the application
    :parameter db: Session: Get the database session
    :return: A message to the user
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        if user.confirmed:
            return {"message": "Your email is already confirmed"}
        background_tasks.add_task(send_email, user.email, user.username, request.base_url,
                                  payload={"subject": "Confirm your email", "template_name": "email_template.html"})
    return {"message": "Check your email for confirmation."}


@router.post('/reset_password')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that will allow them to reset their password. The function takes in a RequestEmail object, which contains the user's email address.
    The function then checks if there is a user associated with that email address and sends an email containing instructions on how to reset their password.

    :parameter body: RequestEmail: Get the email from the request body
    :parameter background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :parameter request: Request: Get the base url of the application
    :parameter db: Session: Get the database session
    :return: A message, depending on the email address entered
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url,
                                  payload={"subject": "Confirmation", "template_name": "reset_password.html"})
        return {"message": "Check your email for the next step."}
    return {"message": "Your email is incorrect"}


@router.get('/password_reset_confirm/{token}')
async def password_reset_confirm(token: str, db: Session = Depends(get_db)):
    """
    The password_reset_confirm function is used to reset a user's password.
        It takes in the token from the email sent to the user and returns a new token that can be used by the client to update their password.

    :parameter token: str: Get the email from the token
    :parameter db: Session: Get the database session
    :return: A reset_password_token
    :doc-author: Trelent
    """
    email = auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    reset_password_token = auth_service.create_email_token(data={"sub": user.email})
    await repository_users.update_reset_token(user, reset_password_token, db)
    return {'reset_password_token': reset_password_token}


@router.post('/set_new_password')
async def update_password(request: ResetPassword, db: Session = Depends(get_db)):
    """
    The update_password function takes a ResetPassword object and updates the user's password.
    It first checks if the reset_password_token is valid, then it checks if the new password matches the confirm password field. If both of these are true, it will update the user's password with the new one.

    :parameter request: ResetPassword: Get the reset_password_token and new password from the user
    :parameter db: Session: Get the database session
    :return: A message
    :doc-author: Trelent
    """
    token = request.reset_password_token
    email = auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    check_token = user.password_reset_token
    if check_token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid reset token")
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="passwords do not match")

    new_password = auth_password.get_hash_password(request.new_password)
    await repository_users.update_password(user, new_password, db)
    await repository_users.update_reset_token(user, None, db)
    return {"message": "Password successfully updated"}
