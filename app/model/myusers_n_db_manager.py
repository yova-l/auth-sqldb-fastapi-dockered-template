from configparser import ConfigParser
from pydantic import BaseModel
from typing import Optional
import psycopg2
import logging
import os
from email_validator import validate_email, EmailNotValidError


def _config(filename=None, section='postgresql'):
    # Use the correct file path
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), '..', '..','database.ini')
        
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def process_user(dbres):
        # For now let's assume only one page is associated to the user (BAD, need to scale)
        # MEans that dbres len == 1
        usrname, fullname, mail, hashed_pass, disabled, hashed_notion_token, page_id = dbres[0]
        return UserInDB(
            username = usrname,
            email = mail,
            full_name = fullname,
            disabled = disabled,
            notion_token = hashed_notion_token,
            permitted_pages = {page_id},
            hashed_password = hashed_pass
        )


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    notion_token: str | None = None
    permitted_pages: set[str] | None = None


class UserInDB(User):
    hashed_password: str


class SqlDbManager(BaseModel):
    connection_params: dict[str, str] = _config()
    
    def register_user(self, 
                      username: str, 
                      email: str, 
                      hashed_password: str, 
                      hashed_notion_token: str, 
                      disabled: Optional[bool] = False, 
                      full_name: Optional[str] = None):
        # Setup logging
        logging.basicConfig(filename='./logs/db_errors.log', level=logging.ERROR)

        if not validate_email(email, check_deliverability=True):
            raise EmailNotValidError

        try:
            # Establishing the connection
            connection = psycopg2.connect(**self.connection_params)
            cursor = connection.cursor()
            
            # SQL INSERT statement
            insert_query = """
            INSERT INTO public."user"(
            username, full_name, email, hashed_password, disabled, hashed_notion_token)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            
            # Data to be inserted
            data = (username, full_name, email, hashed_password, disabled, hashed_notion_token)
            
            # Executing the INSERT statement
            cursor.execute(insert_query, data)
            
            # Committing the transaction
            connection.commit()
            
        except psycopg2.Error as e:
            # Log error message
            logging.error(f"Database error: {e.pgcode} - {e.pgerror}")
            print(f"An error occurred: {e.pgcode} - {e.pgerror}")
            
        finally:
            # Closing the cursor and connection
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

    def get_user(self, username: str):
        # SQL INJECTEION VULNERABLE, TO DO
        postgreSQL_select_Query = f"""
        SELECT username, full_name, email, hashed_password, disabled, hashed_notion_token, public."permitted_pages".page_id
        FROM public."user" 
        JOIN public."permitted_pages" ON public."user".id = public."permitted_pages".user_id
        WHERE username='{username}';
        """
        try:
            # Establishing the connection
            connection = psycopg2.connect(**self.connection_params)
            cursor = connection.cursor()  
            cursor.execute(postgreSQL_select_Query)
            records = cursor.fetchall()
            print(records)
            
            # Committing the transaction
            connection.commit()  
        except psycopg2.Error as e:
            # Log error message
            logging.error(f"Database error: {e.pgcode} - {e.pgerror}")
            print(f"An error occurred: {e.pgcode} - {e.pgerror}")
        finally:
            # Closing the cursor and connection
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return records

    def register_users(self):
        pass

    def insert_permitted_page(user_id, page_id):
        pass
