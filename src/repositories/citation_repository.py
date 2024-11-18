from config import db
from sqlalchemy import text

from entities.citation import Article
from util import citation_data_to_class


def get_citations():
    citations = db.session.execute(
        text(
            """
            SELECT * FROM citation_base 
            INNER JOIN articles 
            ON citation_base.id = articles.citation_id
            """
        )
    ).mappings()
    return [citation_data_to_class(dict(c)) for c in citations]


def create_citation(citation_class):
    """
    Insert citation into database.
    :return: success message or raise error
    """
    try:
        # Insert to citation_base
        citation_base_sql = text(
            """
            INSERT INTO citation_base (key, type, created_at)
            VALUES (:key, :type, :created_at)
            RETURNING id
        """
        )
        result = db.session.execute(
            citation_base_sql,
            {
                "key": citation_class.key,
                "type": citation_class.type,
                "created_at": citation_class.created_at,
            },
        )
        citation_base_id = result.fetchone()[0]

        # Insert to articles
        if isinstance(citation_class, Article):
            article_sql = text(
                """
                INSERT INTO articles (citation_id, author, title, journal, year, volume, number, pages, month, note)
                VALUES (:citation_id, :author, :title, :journal, :year, :volume, :number, :pages, :month, :note)
                """
            )
            db.session.execute(
                article_sql,
                {
                    "citation_id": citation_base_id,
                    "author": citation_class.author,
                    "title": citation_class.title,
                    "journal": citation_class.journal,
                    "year": citation_class.year,
                    "volume": citation_class.volume,
                    "number": citation_class.number,
                    "pages": citation_class.pages,
                    "month": citation_class.month,
                    "note": citation_class.note,
                },
            )

        db.session.commit()

    except Exception as e:
        db.session.rollback
        print(e)
        return False

    return True
