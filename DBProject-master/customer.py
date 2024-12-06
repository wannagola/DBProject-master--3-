# customer.py

from sqlalchemy import Column, String, Numeric, func
from sqlalchemy.orm import relationship
from models import Base, Session, TaxBracket  # TaxBracket 임포트
from consultant import Consultant
from other_models import (
    CustomerIncomeList, CustomerRequest, ConsultantEvaluation,
    BanList, ConsultantRespond, CustomerFamily
)
import random
import string

class Customer(Base):
    __tablename__ = 'customer'

    id = Column(String(15), primary_key=True)
    password = Column(String(15), nullable=False)
    telephone = Column(Numeric(11, 0), nullable=False)
    email = Column(String(50), nullable=False)
    fullname = Column(String(5), nullable=False)
    expected_tax = Column(Numeric(10, 0), nullable=True)
    verification = Column(String(10), unique=True, nullable=True)

    income_list = relationship('CustomerIncomeList', back_populates='customer', uselist=False)
    evaluations = relationship('ConsultantEvaluation', back_populates='customer')
    requests = relationship('CustomerRequest', back_populates='customer')
    family = relationship('CustomerFamily', back_populates='customer', passive_deletes=True)

    @classmethod
    def register(cls, id, password, telephone, email, fullname):
        session = Session()
        try:
            with session.begin():
                new_customer = cls(
                    id=id,
                    password=password,
                    telephone=telephone,
                    email=email,
                    fullname=fullname
                )
                session.add(new_customer)
            print(f"{id} 고객님! 성공적으로 회원가입 되었습니다.")
        except Exception as e:
            session.rollback()
            print(f"회원가입 중 오류 발생: {e}")
        finally:
            session.close()

    @classmethod
    def login(cls, id, password):
        session = Session()
        try:
            customer = session.query(cls).filter_by(id=id).first()
            if customer:
                if customer.password == password:
                    print(f"환영합니다. {id} 고객님!")
                    return customer
                else:
                    print("비밀번호가 일치하지 않습니다.")
            else:
                print("일치하는 아이디가 존재하지 않습니다.")
        except Exception as e:
            print(f"로그인 중 오류 발생: {e}")
        finally:
            session.close()
        return None

    # 소득 정보 입력 메서드
    def input_income(self):
        session = Session()
        try:
            with session.begin():
                self._get_income_input(session)
                self.calculate_expected_tax(session)
        except Exception as e:
            session.rollback()
            print(f"오류 발생: {e}")
        finally:
            session.close()

    def _get_income_input(self, session):
        print("소득 정보를 입력합니다. 값을 입력하지 않으면 기본값 0이 저장됩니다.")
        interest = input("이자 소득: ") or '0'
        dividend = input("배당 소득: ") or '0'
        business = input("사업 소득: ") or '0'
        earned = input("근로 소득: ") or '0'
        pension = input("연금 소득: ") or '0'
        other = input("기타 소득: ") or '0'

        income = CustomerIncomeList(
            id=self.id,
            interest=interest,
            dividend=dividend,
            business=business,
            earned=earned,
            pension=pension,
            other=other
        )
        session.merge(income)  # 이미 존재하면 업데이트
        print("소득 정보가 저장되었습니다.")

    # 부양 가족 정보 입력 메서드
    def input_family_info(self):
        session = Session()
        try:
            with session.begin():
                self._get_family_input(session)
        except Exception as e:
            session.rollback()
            print(f"오류 발생: {e}")
        finally:
            session.close()

    def _get_family_input(self, session):
        print("부양 가족 정보를 입력합니다.")
        family_user_name = input("가족 사용자 이름: ")
        family_data = CustomerFamily(
            id=self.id,
            family_user_name=family_user_name
        )
        session.merge(family_data)
        print("부양 가족 정보가 저장되었습니다.")

    # 가족 인증번호 생성 메서드
    def generate_verification_code(self):
        session = Session()
        try:
            with session.begin():
                verification_code = ''.join(random.choices(string.digits, k=6))
                customer = session.query(Customer).filter_by(id=self.id).first()
                customer.verification = verification_code
                print(f"가족 인증번호가 생성되었습니다: {verification_code}")
        except Exception as e:
            session.rollback()
            print(f"오류 발생: {e}")
        finally:
            session.close()

    # 컨설턴트 평가 작성 메서드
    def write_evaluation(self):
        session = Session()
        try:
            with session.begin():
                # 고객이 받은 제안서 목록 조회
                proposals = session.query(ConsultantRespond).filter_by(id=self.id).all()
                if not proposals:
                    print("받은 제안서가 없습니다.")
                    return

                print("\n***** 받은 제안서 목록 *****\n")
                for idx, proposal in enumerate(proposals, start=1):
                    consultant = session.query(Consultant).filter_by(cid=proposal.cid).first()
                    if consultant:
                        print(f"{idx}. 컨설턴트 이름: {consultant.fullname} (ID: {consultant.cid})")
                    else:
                        print(f"{idx}. 컨설턴트 ID: {proposal.cid}")

                choice = input("평가할 컨설턴트의 번호를 입력하세요 (취소하려면 0 입력): ")
                try:
                    selected_index = int(choice) - 1
                    if choice == '0':
                        return
                    if 0 <= selected_index < len(proposals):
                        selected_proposal = proposals[selected_index]
                        evaluation_text = input("컨설턴트에 대한 평가를 입력하세요: ")
                        evaluation = ConsultantEvaluation(
                            id=self.id,
                            cid=selected_proposal.cid,
                            evaluation_text=evaluation_text
                        )
                        session.add(evaluation)
                        print("평가가 저장되었습니다.")
                    else:
                        print("잘못된 번호입니다.")
                except ValueError:
                    print("유효한 번호를 입력하세요.")
        except Exception as e:
            session.rollback()
            print(f"평가 작성 중 오류 발생: {e}")
        finally:
            session.close()

    # 요청 글 작성 메서드
    def write_request(self):
        session = Session()
        try:
            with session.begin():
                self._get_request_input(session)
        except Exception as e:
            session.rollback()
            print(f"오류 발생: {e}")
        finally:
            session.close()

    def _get_request_input(self, session):
        title = input("요청 제목: ")
        request_text = input("요청 내용: ")
        request = CustomerRequest(
            id=self.id,
            title=title,
            request_text=request_text
        )
        session.add(request)
        print("요청 글이 저장되었습니다.")

    # 요청 글 삭제 메서드
    def delete_request(self):
        session = Session()
        try:
            with session.begin():
                # 고객이 작성한 요청 글 목록을 가져옵니다.
                requests = session.query(CustomerRequest).filter_by(id=self.id).all()
                if not requests:
                    print("등록된 요청 글이 없습니다.")
                    return

                # 작성한 요청 글 목록을 번호와 함께 표시합니다.
                print("\n***** 등록된 요청 글 목록 *****\n")
                for idx, req in enumerate(requests, start=1):
                    print(f"{idx}. 제목: {req.title}")
                    print(f"   내용: {req.request_text}\n")

                # 삭제할 요청 글의 번호를 입력받습니다.
                choice = input("삭제할 요청 글의 번호를 입력하세요 (취소하려면 0 입력): ")
                print()
                try:
                    selected_index = int(choice) - 1
                    if choice == '0':
                        return
                    if 0 <= selected_index < len(requests):
                        selected_request = requests[selected_index]
                        confirmation = input(f"'{selected_request.title}' 요청 글을 삭제하시겠습니까? (y/n): ").lower()
                        if confirmation == 'y':
                            session.delete(selected_request)
                            print("요청 글이 삭제되었습니다.")
                        else:
                            print("삭제가 취소되었습니다.")
                    else:
                        print("잘못된 번호입니다.")
                except ValueError:
                    print("유효한 번호를 입력하세요.")
        except Exception as e:
            session.rollback()
            print(f"요청 글 삭제 중 오류 발생: {e}")
        finally:
            session.close()

    # 부양 가족 관리 메서드
    def manage_family_users(self):
        session = Session()
        try:
            with session.begin():
                family_users = session.query(CustomerFamily).filter_by(id=self.id).all()
                if not family_users:
                    print("등록된 부양 가족이 없습니다.")
                    return

                # 부양 가족 목록 표시
                print("\n***** 부양 가족 목록 *****\n")
                for idx, family in enumerate(family_users, start=1):
                    print(f"{idx}. 이름: {family.family_user_name}")
                    print(f"   공제 금액: {family.deduction if family.deduction else 0}\n")

                # 삭제할 부양 가족의 번호를 입력받음
                choice = input("삭제할 부양 가족의 번호를 입력하세요 (취소하려면 0 입력): ")
                print()
                try:
                    selected_index = int(choice) - 1
                    if choice == '0':
                        return
                    if 0 <= selected_index < len(family_users):
                        selected_family = family_users[selected_index]
                        confirmation = input(f"'{selected_family.family_user_name}' 부양 가족을 삭제하시겠습니까? (y/n): ").lower()
                        if confirmation == 'y':
                            session.delete(selected_family)
                            print("부양 가족이 삭제되었습니다.")
                        else:
                            print("삭제가 취소되었습니다.")
                    else:
                        print("잘못된 번호입니다.")
                except ValueError:
                    print("유효한 번호를 입력하세요.")
        except Exception as e:
            session.rollback()
            print(f"부양 가족 관리 중 오류 발생: {e}")
        finally:
            session.close()

    # 제안서 선택 메서드
    def select_proposal(self):
        session = Session()
        try:
            with session.begin():
                self._select_proposal_flow(session)
        except Exception as e:
            session.rollback()
            print(f"오류 발생: {e}")
        finally:
            session.close()

    def _select_proposal_flow(self, session):
        requests = session.query(CustomerRequest).filter_by(id=self.id).all()
        if not requests:
            print("등록된 요청 글이 없습니다.")
            return
        self._display_requests(requests)
        print()
        choice = input("제안서를 확인할 요청 글의 번호를 입력하세요 : ")
        print()
        try:
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(requests):
                request = requests[selected_index]
                self._handle_request_responses(session, request)
            else:
                print("잘못된 번호입니다.")
        except ValueError:
            print("유효한 번호를 입력하세요.")

    def _display_requests(self, requests):
        print("***** 등록된 요청 글 목록 *****")
        print()
        for idx, req in enumerate(requests, start=1):
            print(f"{idx}. 요청 제목: {req.title}")

    def _handle_request_responses(self, session, request):
        # 차단된 컨설턴트의 제안서 제외
        blocked_cids = session.query(BanList.cid).filter(BanList.id == self.id).subquery()
        responds = session.query(ConsultantRespond).filter(
            ConsultantRespond.id == request.id,
            ConsultantRespond.title == request.title,
            ~ConsultantRespond.cid.in_(blocked_cids)
        ).all()

        if not responds:
            print("받은 제안서가 없습니다.")
            return
        index = 0
        while True:
            self._display_responses(responds, index)
            choice = input("자세히 볼 제안서 번호를 입력하세요 (+ 입력 시 다음 5개 표시 / - 입력시 이전 5개 표시 / 0 입력 시 종료) : ")

            if choice == '+':
                index += 5
                if index >= len(responds):
                    print("더 이상 표시할 제안서가 없습니다.")
                    index -= 5
                continue
            elif choice == '-':
                index -= 5
                if index < 0:
                    index = 0
            elif choice == '0':
                break
            else:
                try:
                    selected_index = int(choice) - 1
                    if 0 <= selected_index < len(responds):
                        respond = responds[selected_index]
                        consultant = session.query(Consultant).filter_by(cid=respond.cid).first()
                        self.respond_options(respond, consultant)
                    else:
                        print("잘못된 번호입니다.")
                except ValueError:
                    print("유효한 번호를 입력하세요.")

    def _display_responses(self, responds, index):
        print("***** 제안서 목록 *****")
        print()
        for idx in range(index, min(index + 5, len(responds))):
            respond = responds[idx]
            consultant = respond.consultant
            if consultant:
                print(f"{idx + 1}. 컨설턴트 이름: {consultant.fullname}")
            else:
                print(f"{idx + 1}. 컨설턴트 이름: 알 수 없음")
        print()

    def respond_options(self, respond, consultant):
        print(f"\n선택한 제안서 내용:\n{respond.respond_text}")
        print()
        while True:
            print("1번: 컨설턴트 자기소개서 보기")
            print("2번: 컨설턴트 선택하기")
            print("3번: 컨설턴트 차단하기")
            print("0번: 되돌아가기")
            action = input("원하는 기능의 번호를 입력하세요: ")
            print()
            if action == '1':
                if consultant:
                    explain = consultant.explain
                    if explain:
                        print(f"\n컨설턴트 {consultant.fullname}의 자기소개서:\n {explain.explain_text}")
                        print()
                    else:
                        print("자기소개서가 없습니다.")
                else:
                    print("컨설턴트 정보가 없습니다.")
            elif action == '2':
                if consultant:
                    print(f"컨설턴트 {consultant.fullname}를 선택하였습니다.")
                    # 추가적인 선택 로직 구현 가능
                else:
                    print("컨설턴트 정보가 없습니다.")
                return
            elif action == '3':
                if consultant:
                    confirmation = input(f"정말로 컨설턴트 {consultant.fullname}를 차단하시겠습니까? (y/n): ").lower()
                    if confirmation == 'y':
                        self.block_consultant_specific(consultant.cid)
                        print(f"컨설턴트 {consultant.fullname}가 차단되었습니다.")
                        return  # 차단 후 제안서 보기 종료
                    else:
                        print("차단이 취소되었습니다.")
                else:
                    print("컨설턴트 정보가 없습니다.")
            elif action == '0':
                break
            else:
                print("잘못된 입력입니다.")

    def block_consultant_specific(self, cid):
        session = Session()
        try:
            with session.begin():
                blocked = session.query(BanList).filter_by(id=self.id, cid=cid).first()
                if blocked:
                    print(f"이미 컨설턴트 {cid}를 차단하였습니다.")
                else:
                    blocked = BanList(
                        id=self.id,
                        cid=cid
                    )
                    session.add(blocked)
                    print(f"컨설턴트 {cid}를 차단하였습니다.")
        except Exception as e:
            session.rollback()
            print(f"컨설턴트 차단 중 오류 발생: {e}")
        finally:
            session.close()

    def unblock_consultant_specific(self, cid):
        session = Session()
        try:
            with session.begin():
                blocked = session.query(BanList).filter_by(id=self.id, cid=cid).first()
                if blocked:
                    session.delete(blocked)
                    print(f"컨설턴트 {cid}의 차단을 해제하였습니다.")
                else:
                    print(f"컨설턴트 {cid}는 이미 차단되지 않았습니다.")
        except Exception as e:
            session.rollback()
            print(f"컨설턴트 차단 해제 중 오류 발생: {e}")
        finally:
            session.close()

    # 차단된 컨설턴트 관리 메서드
    def manage_blocked_consultants(self):
        session = Session()
        try:
            with session.begin():
                blocked_consultants = session.query(BanList).filter_by(id=self.id).all()
                if not blocked_consultants:
                    print("현재 차단된 컨설턴트가 없습니다.")
                    return
                print("\n***** 차단된 컨설턴트 목록 *****\n")
                for idx, ban in enumerate(blocked_consultants, start=1):
                    consultant = session.query(Consultant).filter_by(cid=ban.cid).first()
                    if consultant:
                        print(f"{idx}. 컨설턴트 ID: {consultant.cid}, 이름: {consultant.fullname}")
                    else:
                        print(f"{idx}. 컨설턴트 ID: {ban.cid}, 이름: 알 수 없음")
                print()
                choice = input("차단을 해제할 컨설턴트의 번호를 입력하세요 (취소하려면 0 입력): ")
                print()
                try:
                    selected_index = int(choice) - 1
                    if choice == '0':
                        return
                    if 0 <= selected_index < len(blocked_consultants):
                        ban = blocked_consultants[selected_index]
                        consultant = session.query(Consultant).filter_by(cid=ban.cid).first()
                        if consultant:
                            confirmation = input(f"컨설턴트 {consultant.fullname}의 차단을 해제하시겠습니까? (y/n): ").lower()
                            if confirmation == 'y':
                                self.unblock_consultant_specific(consultant.cid)
                        else:
                            confirmation = input(f"컨설턴트 ID {ban.cid}의 차단을 해제하시겠습니까? (y/n): ").lower()
                            if confirmation == 'y':
                                self.unblock_consultant_specific(ban.cid)
                    else:
                        print("잘못된 번호입니다.")
                except ValueError:
                    print("유효한 번호를 입력하세요.")
        except Exception as e:
            session.rollback()
            print(f"차단된 컨설턴트 관리 중 오류 발생: {e}")
        finally:
            session.close()

    # 예상 세금 계산 메서드
    def calculate_expected_tax(self, session):
        # 세션 내에서 현재 고객을 다시 쿼리
        customer = session.query(Customer).filter_by(id=self.id).first()
        income = customer.income_list
        if not income:
            print("소득 정보가 없습니다. 먼저 소득 정보를 입력하세요.")
            return

        # 소득 합산
        total_income = sum([
            float(income.interest) if income.interest else 0,
            float(income.dividend) if income.dividend else 0,
            float(income.business) if income.business else 0,
            float(income.earned) if income.earned else 0,
            float(income.pension) if income.pension else 0,
            float(income.other) if income.other else 0
        ])

        # 부양 가족 공제 금액 계산
        family_deductions = session.query(func.sum(CustomerFamily.deduction)).filter_by(id=customer.id).scalar()
        if not family_deductions:
            family_deductions = 0
        else:
            family_deductions = float(family_deductions)  # decimal.Decimal을 float으로 변환

        # 과세표준 계산
        taxable_income = total_income - family_deductions
        taxable_income = max(taxable_income, 0)  # 과세표준은 음수가 될 수 없음

        # 세율표를 데이터베이스에서 가져오기
        tax_brackets = session.query(TaxBracket).order_by(TaxBracket.upper_limit).all()

        if not tax_brackets:
            print("세율표가 설정되지 않았습니다. 관리자에게 문의하세요.")
            return

        # 세금 계산
        tax = 0
        for bracket in tax_brackets:
            if taxable_income <= bracket.upper_limit:
                tax = taxable_income * float(bracket.rate) - float(bracket.deduction)
                break

        # 결과 출력
        tax = max(tax, 0)  # 세금은 음수가 될 수 없음
        print(f"총 소득 금액: {total_income:,.0f}원")
        print(f"부양 가족 공제 금액: {family_deductions:,.0f}원")
        print(f"과세 표준: {taxable_income:,.0f}원")
        print(f"예상 세액: {tax:,.0f}원")

        # 예상 세액을 데이터베이스에 저장
        customer.expected_tax = tax
        session.commit()