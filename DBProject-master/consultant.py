# consultant.py

from sqlalchemy import Column, String, Numeric, select
from sqlalchemy.orm import relationship, joinedload
from models import Base, Session
from other_models import ConsultantExplain, ConsultantRespond, CustomerRequest, BanList

class Consultant(Base):
    __tablename__ = 'consultant'

    cid = Column(String(15), primary_key=True)
    password = Column(String(15), nullable=False)
    telephone = Column(Numeric(11, 0), nullable=False)
    email = Column(String(50), nullable=False)
    fullname = Column(String(5), nullable=False)
    certification = Column(String(10), nullable=False)

    evaluations = relationship('ConsultantEvaluation', back_populates='consultant')
    explain = relationship('ConsultantExplain', back_populates='consultant', uselist=False)
    responds = relationship('ConsultantRespond', back_populates='consultant')

    @classmethod
    def register(cls, cid, password, telephone, email, fullname, certification):
        session = Session()
        try:
            with session.begin():
                new_consultant = cls(
                    cid=cid,
                    password=password,
                    telephone=telephone,
                    email=email,
                    fullname=fullname,
                    certification=certification
                )
                session.add(new_consultant)
            print(f"Consultant {cid} registered successfully.")
        except Exception as e:
            session.rollback()
            print(f"회원가입 중 오류 발생: {e}")
        finally:
            session.close()

    @classmethod
    def login(cls, cid, password):
        session = Session()
        try:
            consultant = session.query(cls).filter_by(cid=cid).first()
            if consultant:
                if consultant.password == password:
                    print(f"컨설턴트 {cid} 환영합니다.")
                    return consultant
                else:
                    print("비밀번호가 일치하지 않습니다.")
            else:
                print("일치하는 아이디가 존재하지 않습니다.")
        except Exception as e:
            print(f"로그인 중 오류 발생: {e}")
        finally:
            session.close()
        return None

    # 자기소개 작성 및 수정 메서드
    def write_explain(self):
        with Session() as session:
            try:
                with session.begin():
                    self._get_explain_input(session)
            except Exception as e:
                session.rollback()
                print(f"오류 발생: {e}")

    def _get_explain_input(self, session):
        explain_text = input("자기소개 내용을 입력하세요: ")
        explain = ConsultantExplain(
            cid=self.cid,
            explain_text=explain_text
        )
        session.merge(explain)  # 이미 존재하면 업데이트
        print("자기소개가 저장되었습니다.")

    # 요청 글에 제안서 작성 메서드
    def write_proposal(self):
        with Session() as session:
            try:
                with session.begin():
                    self._proposal_flow(session)
            except Exception as e:
                session.rollback()
                print(f"오류 발생: {e}")

    def _proposal_flow(self, session):
        offset = 0
        while True:
            # 차단된 고객 제외
            blocked_customers = session.query(BanList.id).filter(BanList.cid == self.cid).subquery()

            # IN 절에 subquery 사용 및 관계 조인
            requests = session.query(CustomerRequest)\
                .filter(~CustomerRequest.id.in_(blocked_customers))\
                .options(joinedload(CustomerRequest.responds).joinedload(ConsultantRespond.consultant))\
                .offset(offset)\
                .limit(10)\
                .all()

            if not requests:
                print("더 이상 표시할 요청 글이 없습니다.")
                print()
                offset -= 10
                continue

            self._display_requests(requests)
            print()
            choice = input("제안서를 작성할 요청 글의 번호를 입력하세요 (+ 입력 시 다음 10개 표시 / - 입력 시 이전 10개 표시 / 0 입력시 종료) : ")
            print()
            if choice == '+':
                offset += 10
                continue
            elif choice == '-':
                offset -= 10
                if(offset < 0):
                    print("첫 페이지 입니다.")
                    offset = 0
            elif choice == '0':
                break
            else:
                try:
                    selected_index = int(choice) - 1
                    if 0 <= selected_index < len(requests):
                        request = requests[selected_index]
                        if self._is_blocked(session, request.id):
                            print("이 고객은 당신을 차단하였습니다.")
                        else:
                            self._create_proposal(session, request.id, request.title)
                            break  # 제안서 작성 후 종료
                    else:
                        print("잘못된 번호입니다.")
                except ValueError:
                    print("유효한 번호를 입력하세요.")

    def _display_requests(self, requests):
        print()
        print(" ***** 등록된 요청 글 목록 *****")
        print()
        for idx, req in enumerate(requests, start=1):
            print(f"{idx}. 요청 제목: {req.title} 작성자 아이디: {req.id}")

    def _is_blocked(self, session, customer_id):
        blocked = session.query(BanList).filter_by(id=customer_id, cid=self.cid).first()
        return blocked is not None

    def _create_proposal(self, session, customer_id, title):
        respond_text = input("제안서 내용을 입력하세요: ")
        respond = ConsultantRespond(
            id=customer_id,
            title=title,
            cid=self.cid,
            respond_text=respond_text
        )
        session.add(respond)
        print("제안서가 저장되었습니다.")