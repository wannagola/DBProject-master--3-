# other_models.py

from sqlalchemy import Column, String, Numeric, ForeignKey, ForeignKeyConstraint, and_
from sqlalchemy.orm import relationship
from models import Base

# 고객 소득 정보
class CustomerIncomeList(Base):
    __tablename__ = 'customer_income_list'

    id = Column(String(15), ForeignKey('customer.id', ondelete='CASCADE'), primary_key=True)
    interest = Column(Numeric(10, 0))
    dividend = Column(Numeric(10, 0))
    business = Column(Numeric(10, 0))
    earned = Column(Numeric(10, 0))
    pension = Column(Numeric(10, 0))
    other = Column(Numeric(10, 0))

    customer = relationship('Customer', back_populates='income_list')

# 컨설턴트 평가
class ConsultantEvaluation(Base):
    __tablename__ = 'consultant_evaluation'

    id = Column(String(15), ForeignKey('customer.id', ondelete='CASCADE'), primary_key=True)
    cid = Column(String(15), ForeignKey('consultant.cid', ondelete='CASCADE'), primary_key=True)
    evaluation_text = Column(String(500))

    customer = relationship('Customer', back_populates='evaluations')
    consultant = relationship('Consultant', back_populates='evaluations')

# 고객 요청 글
class CustomerRequest(Base):
    __tablename__ = 'customer_request'

    id = Column(String(15), ForeignKey('customer.id', ondelete='CASCADE'), primary_key=True)
    title = Column(String(100), primary_key=True)
    request_text = Column(String(500))

    customer = relationship('Customer', back_populates='requests')
    responds = relationship(
        'ConsultantRespond',
        back_populates='request',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

# 차단된 컨설턴트 목록
class BanList(Base):
    __tablename__ = 'ban_list'

    id = Column(String(15), ForeignKey('customer.id', ondelete='CASCADE'), primary_key=True)
    cid = Column(String(15), ForeignKey('consultant.cid', ondelete='CASCADE'), primary_key=True)

    customer = relationship('Customer')
    consultant = relationship('Consultant')

# 컨설턴트 자기소개
class ConsultantExplain(Base):
    __tablename__ = 'consultant_explain'

    cid = Column(String(15), ForeignKey('consultant.cid', ondelete='CASCADE'), primary_key=True)
    explain_text = Column(String(500))

    consultant = relationship('Consultant', back_populates='explain')

# 컨설턴트 제안서 (응답)
class ConsultantRespond(Base):
    __tablename__ = 'consultant_respond'

    id = Column(String(15), primary_key=True)
    title = Column(String(100), primary_key=True)
    cid = Column(String(15), ForeignKey('consultant.cid', ondelete='CASCADE'), primary_key=True)
    respond_text = Column(String(500))

    __table_args__ = (
        ForeignKeyConstraint(
            ['id', 'title'],
            ['customer_request.id', 'customer_request.title'],
            ondelete='CASCADE'
        ),
    )

    request = relationship(
        'CustomerRequest',
        back_populates='responds',
        primaryjoin="and_(ConsultantRespond.id==CustomerRequest.id, ConsultantRespond.title==CustomerRequest.title)",
        passive_deletes=True
    )
    consultant = relationship('Consultant', back_populates='responds')

# 고객 가족 정보
class CustomerFamily(Base):
    __tablename__ = 'customer_family'

    id = Column(String(15), ForeignKey('customer.id', ondelete='CASCADE'), primary_key=True)
    family_user_name = Column(String(15), primary_key=True)
    deduction = Column(Numeric(9, 0))

    customer = relationship('Customer', back_populates='family', passive_deletes=True)