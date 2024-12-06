# main.py

from models import Base, engine, Session
from customer import Customer
from consultant import Consultant
from manager import Manager
from family import FamilyUser
from other_models import Base as OtherBase
from other_models import CustomerFamily

# 테이블 생성
Base.metadata.create_all(engine)
OtherBase.metadata.create_all(engine)

def customer_menu(customer):
    while True:
        print("\n--- 고객 메뉴 ---")
        print("1. 소득 정보 입력")
        print("2. 부양 가족 정보 입력")
        print("3. 컨설턴트 평가 작성")
        print("4. 요청 글 작성")
        print("5. 컨설턴트 제안서 확인 및 선택")
        print("6. 차단한 컨설턴트 확인")
        print("7. 예상 세금 계산")
        print("8. 작성한 글 삭제")
        print("9. 부양 가족 관리")  # 새로운 메뉴 옵션 추가
        print("0. 로그아웃")
        choice = input("원하는 기능의 번호를 입력하세요: ")
        print()
        if choice == '1':
            customer.input_income()
        elif choice == '2':
            customer.input_family_info()
            customer.generate_verification_code()
        elif choice == '3':
            customer.write_evaluation()
        elif choice == '4':
            customer.write_request()
        elif choice == '5':
            customer.select_proposal()
        elif choice == '6':
            customer.manage_blocked_consultants()
        elif choice == '7':
            # 예상 세금 계산을 위한 새로운 세션 사용
            session = Session()
            try:
                with session.begin():
                    customer.calculate_expected_tax(session)
            except Exception as e:
                session.rollback()
                print(f"예상 세금 계산 중 오류 발생: {e}")
            finally:
                session.close()
        elif choice == '8':
            customer.delete_request()
        elif choice == '9':
            customer.manage_family_users()  # 부양 가족 관리 기능 추가
        elif choice == '0':
            print("로그아웃합니다.")
            break
        else:
            print("잘못된 입력입니다.")

def consultant_menu(consultant):
    while True:
        print("\n--- 컨설턴트 메뉴 ---")
        print("1. 자기소개 작성/수정")
        print("2. 요청 글에 제안서 작성")
        print("0. 로그아웃")
        choice = input("원하는 기능의 번호를 입력하세요: ")
        print()
        if choice == '1':
            consultant.write_explain()
        elif choice == '2':
            consultant.write_proposal()
        elif choice == '0':
            print("로그아웃합니다.")
            break
        else:
            print("잘못된 입력입니다.")

def manager_menu(manager):
    while True:
        print("\n--- 관리자 메뉴 ---")
        print("1. 세금 계산 규칙 최신화")
        print("2. 컨설턴트 자격증 검토 및 인증")
        print("3. 사용자 평가 관리")
        print("0. 로그아웃")
        choice = input("원하는 기능의 번호를 입력하세요: ")
        print()
        if choice == '1':
            idx = 0
            while True:
                idx += 1
                print(f"{idx} 번째 세율을 소득 수준, 세율, 감액 순으로 입력해 주세요 (각 값을 입력할 때 0을 입력하시면 종료합니다.)")
                upper_limit = input("소득 수준 : ")
                rate = input("세율 : ")
                if upper_limit == '0' or rate == '0':
                    break
                deduction = input("감액 : ")
                manager.update_tax_bracket(idx, upper_limit, rate, deduction)
        elif choice == '2':
            print("컨설턴트 자격증 검토 및 인증 기능은 아직 구현되지 않았습니다.")
        elif choice == '3':
            print("사용자 평가 관리 기능은 아직 구현되지 않았습니다.")
        elif choice == '0':
            print("로그아웃합니다.")
            break
        else:
            print("잘못된 입력입니다.")

def family_user_menu(family_user):
    while True:
        print("\n--- 가족 사용자 메뉴 ---")
        print("1. 부양 가족 공제 금액 입력")
        print("0. 로그아웃")
        choice = input("원하는 기능의 번호를 입력하세요: ")
        print()
        if choice == '1':
            family_user.input_family_info()
        elif choice == '0':
            print("로그아웃합니다.")
            break
        else:
            print("잘못된 입력입니다.")

def family_user_login():
    username = input("가족 사용자 이름을 입력하세요: ")
    verification_code = input("가족 인증번호를 입력하세요: ")

    session = Session()
    try:
        customer = session.query(Customer).filter_by(verification=verification_code).first()
        if customer:
            family_user = FamilyUser(username=username, customer_id=customer.id)
            family_data = session.query(CustomerFamily).filter_by(
                family_user_name=username, id=customer.id).first()
            if family_data:
                family_user_menu(family_user)
            else:
                print("유효하지 않은 가족 사용자 이름 또는 인증번호입니다.")
        else:
            print("유효하지 않은 가족 인증번호입니다.")
    except Exception as e:
        print(f"로그인 중 오류 발생: {e}")
    finally:
        session.close()

def manager_signup():
    mid = input("매니저 아이디: ")
    fullname = input("이름: ")
    section = input("부서: ")
    Manager.register(mid=mid, fullname=fullname, section=section)

def manager_login():
    mid = input("매니저 아이디를 입력하세요: ")
    manager = Manager.login(mid=mid)
    if manager:
        manager_menu(manager)
    else:
        print("일치하는 아이디가 존재하지 않습니다.")

def main_menu():
    while True:
        print("\n--- 메인 메뉴 ---")
        print("1. 고객 로그인")
        print("2. 컨설턴트 로그인")
        print("3. 가족 사용자 로그인")
        print("4. 고객 회원가입")
        print("5. 컨설턴트 회원가입")
        print("6. 매니저 회원가입")
        print("7. 매니저 로그인")
        print("0. 종료")
        choice = input("원하는 기능의 번호를 입력하세요: ")
        print()
        if choice == '1':
            # 고객 로그인
            id = input("아이디를 입력하세요: ")
            password = input("비밀번호를 입력하세요: ")
            customer = Customer.login(id=id, password=password)
            if customer:
                customer_menu(customer)
        elif choice == '2':
            # 컨설턴트 로그인
            cid = input("아이디를 입력하세요: ")
            password = input("비밀번호를 입력하세요: ")
            consultant = Consultant.login(cid=cid, password=password)
            if consultant:
                consultant_menu(consultant)
        elif choice == '3':
            # 가족 사용자 로그인
            family_user_login()
        elif choice == '4':
            # 고객 회원가입
            id = input("아이디: ")
            password = input("비밀번호: ")
            telephone_input = input("전화번호: ")
            email = input("이메일: ")
            fullname = input("이름: ")
            try:
                telephone = float(telephone_input)
            except ValueError:
                telephone = 0
                print("잘못된 전화번호 입력입니다. 0으로 설정됩니다.")
            Customer.register(
                id=id,
                password=password,
                telephone=telephone,
                email=email,
                fullname=fullname
            )
        elif choice == '5':
            # 컨설턴트 회원가입
            cid = input("아이디: ")
            password = input("비밀번호: ")
            telephone_input = input("전화번호: ")
            email = input("이메일: ")
            fullname = input("이름: ")
            certification = input("자격증 번호: ")
            try:
                telephone = float(telephone_input)
            except ValueError:
                telephone = 0
                print("잘못된 전화번호 입력입니다. 0으로 설정됩니다.")
            Consultant.register(
                cid=cid,
                password=password,
                telephone=telephone,
                email=email,
                fullname=fullname,
                certification=certification
            )
        elif choice == '6':
            # 매니저 회원가입
            manager_signup()
        elif choice == '7':
            # 매니저 로그인
            manager_login()
        elif choice == '0':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다.")

if __name__ == "__main__":
    main_menu()