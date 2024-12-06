# family.py

from models import Session
from other_models import CustomerFamily

class FamilyUser:
    def __init__(self, username, customer_id):
        self.username = username
        self.customer_id = customer_id

    def input_family_info(self):
        session = Session()
        try:
            with session.begin():
                deduction_input = input("공제 금액: ")
                try:
                    deduction = float(deduction_input) if deduction_input else 0
                except ValueError:
                    deduction = 0
                    print("잘못된 입력입니다. 공제 금액을 0으로 설정합니다.")
                
                family_data = CustomerFamily(
                    id=self.customer_id,
                    family_user_name=self.username,
                    deduction=deduction
                )
                session.merge(family_data)
                print("부양 가족 정보가 저장되었습니다.")
        except Exception as e:
            session.rollback()
            print(f"오류 발생: {e}")
        finally:
            session.close()