from datetime import datetime, date
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from src.books.models import Book
from src.books.schemas import BookSchema, BookCreateSchema



class BookService:
    """
    This class provides methods to create, read, update, and delete the books
    """
    async def get_all_books(self, session: AsyncSession):
        """
        Get list of all the books.
        Return:
        list: list of books
        """
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()
    
    async def create_book(self, book_data:BookCreateSchema, session: AsyncSession):
        """
        Create a book.
        Args:
            book_data (BookCreateSchema): data to create new book
        return -> Book: new book created
        """
        print(f"Type: {type(book_data.published_date)}")  # Should be <class 'datetime.date'>
        print(f"Value: {book_data.published_date}")     
        book_data_dict = book_data.model_dump()
        if isinstance(book_data_dict.get('published_date'), date):
            book_data_dict["published_date"] = datetime.strptime(str(book_data_dict['published_date']), "%Y-%m-%d").date()
        new_book = Book(**book_data_dict)
        # new_book.published_date = datetime.strptime(book_data_dict['published_date'], "%Y-%m-%d")
        session.add(new_book)
        await session.commit()

        return new_book
    
    async def get_book(self, book_uid: str, session:AsyncSession):
        """
        Get a book by its UUID.
        Args -> book_uid(str): The UUID of the book.
        Return -> the book object.
        """
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None
    
    async def update_book(self, book_uid: str, update_data: BookSchema,session: AsyncSession):
        """"
        Update a book.
        Args -> 
            book_id(str): UUID of the book to upload.
            update_data (BookCreateSchema): data to update the book.
        Return -> Book : updated book.
        """
        book_to_update = await self.get_book(book_uid, session)
        if book_to_update is not None:
            update_data_dict = update_data.model_dump(exclude_unset=True)
            if isinstance(update_data_dict.get('published_date'), date):
                update_data_dict["published_date"] = datetime.strptime(str(update_data_dict['published_date']), "%Y-%m-%d").date()
            for k,v in update_data_dict.items():
                setattr(book_to_update, k, v)

            await session.commit()
            return book_to_update
        else:
            return None
        
    async def delete_book(self, book_uid:str, session:AsyncSession):
        """
        Delete a book.
        Args -> book_uid (str): the UUID of the book.
        """
        book_to_delete =await self.get_book(book_uid, session)
        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return {"message":f"Book ==> {book_to_delete.title} has been deleted"}
        else:
            return None
        
