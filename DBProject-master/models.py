# models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, Numeric

# 데이터베이스 연결 설정
engine = create_engine('postgresql+psycopg2://project:project@localhost:5432/project_db')
Session = sessionmaker(bind=engine)

# Base 클래스 정의
Base = declarative_base()

# TaxBracket 클래스 추가
class TaxBracket(Base):
    __tablename__ = 'tax_bracket'

    id = Column(String(2), primary_key=True)
    upper_limit = Column(Numeric(15, 2), nullable=False)
    rate = Column(Numeric(5, 4), nullable=False)
    deduction = Column(Numeric(15, 2), nullable=False)