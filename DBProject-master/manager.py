# manager.py

from sqlalchemy import create_engine, Column, Integer, Float, String, Sequence, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from models import Session
from consultant import Consultant
from other_models import ConsultantEvaluation
import psycopg2

Base = declarative_base()

class Manager(Base):
    __tablename__ = 'manager'

    mid = Column(String(15), primary_key=True)
    fullname = Column(String(5), nullable=False)
    section = Column(String(15), nullable=False)

    @classmethod
    def register(cls, mid, fullname, section):
        session = Session()
        try:
            with session.begin():
                new_manager = cls(
                    mid=mid,
                    fullname=fullname,
                    section=section
                )
                session.add(new_manager)
            print(f"Manager {mid} registered successfully.")
        except Exception as e:
            session.rollback()
            print(f"회원가입 중 오류 발생: {e}")
        finally:
            session.close()

    @classmethod
    def login(cls, mid):
        session = Session()
        try:
            manager = session.query(cls).filter_by(mid=mid).first()
            return manager
        except Exception as e:
            print(f"조회 중 오류 발생: {e}")
            return None
        finally:
            session.close()

    @classmethod
    def update_tax_bracket(self, id, upper_limit, rate, deduction):
        try:
            connection = psycopg2.connect(user="project",
                                          password="project",
                                          host="127.0.0.1",
                                          port="5432",
                                          database="project_db")
            cursor = connection.cursor()

            # 세율 정보 업데이트
            update_query = """
            INSERT INTO tax_bracket (id, upper_limit, rate, deduction)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id)
            DO UPDATE SET upper_limit = EXCLUDED.upper_limit, rate = EXCLUDED.rate, deduction = EXCLUDED.deduction;
            """
            cursor.execute(update_query, (id, upper_limit, rate, deduction))
            connection.commit()
            print("Tax bracket updated successfully")
        except (Exception, psycopg2.Error) as error:
            print("Error while updating tax bracket", error)
        finally:
            if connection:
                cursor.close()
                connection.close()

    @classmethod
    def review_consultant_certifications(cls):
        """
        매니저가 컨설턴트들의 자격증(인증 상태)을 검토하고 인증/거절을 결정하는 메서드.
        가정:
        - Consultant 모델에 certification_status 컬럼이 있어 'pending', 'approved', 'rejected' 등의 상태를 가짐.
        """
        session = Session()
        
        try:
            # 인증 대기 중인 컨설턴트 목록 조회
            pending_consultants = session.query(Consultant).filter_by(certification_status='pending').all()

            if not pending_consultants:
                print("인증 대기 중인 컨설턴트가 없습니다.")
                return
            # 목록 표시하기
            print("\n***** 인증 대기 컨설턴트 목록 *****\n")
            for idx, c in enumerate(pending_consultants, start=1):
                print(f"{idx}. ID: {c.cid}, 이름: {c.fullname}")

            choice = input("인증 상태를 변경할 컨설턴트 번호를 입력하세요 (0 입력 시 취소): ")
            if choice == '0':
                return

            try:
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(pending_consultants):
                    selected_consultant = pending_consultants[selected_index]
                    print(f"선택된 컨설턴트: {selected_consultant.fullname} (ID: {selected_consultant.cid})")
                    action = input("1: 인증 승인, 2: 인증 거절, 0: 취소 >> ")
                    if action == '1':
                        selected_consultant.certification_status = 'approved'
                        session.commit()
                        print("컨설턴트 인증이 승인되었습니다.")
                    elif action == '2':
                        selected_consultant.certification_status = 'rejected'
                        session.commit()
                        print("컨설턴트 인증이 거절되었습니다.")
                    elif action == '0':
                        print("취소되었습니다.")
                    else:
                        print("잘못된 입력입니다.")
                else:
                    print("잘못된 번호입니다.")
            except ValueError:
                print("유효한 번호를 입력하세요.")
        except Exception as e:
            session.rollback()
            print(f"인증 검토 중 오류 발생: {e}")
        finally:
            session.close()

    @classmethod
    def view_consultant_evaluations(cls):
        """
        매니저가 사용자들이 작성한 컨설턴트 평가를 컨설턴트별로 그룹화하여 볼 수 있음.
        가정:
        - ConsultantEvaluation: id(고객), cid(컨설턴트), evaluation_text(평가 내용)
        - Consultant : cid, fullname
        """
        session = Session()
        try:
            # 컨설턴트별 평가 개수 조회
            # func.count()를 이용하여 컨설턴트별 평가수 그룹화
            evaluation_counts = session.query(
                ConsultantEvaluation.cid,
                func.count(ConsultantEvaluation.evaluation_text).label('eval_count')
            ).group_by(ConsultantEvaluation.cid).all()

            if not evaluation_counts:
                print("등록된 평가가 없습니다.")
                return

            print("\n***** 컨설턴트별 평가 개수 목록 *****\n")
            for idx, ev in enumerate(evaluation_counts, start=1):
                consultant = session.query(Consultant).filter_by(cid=ev.cid).first()
                consultant_name = consultant.fullname if consultant else "알 수 없음"
                print(f"{idx}. 컨설턴트 ID: {ev.cid}, 이름: {consultant_name}, 평가 개수: {ev.eval_count}")

            choice = input("자세히 볼 컨설턴트 평가 번호를 입력하세요 (0 입력 시 취소): ")
            if choice == '0':
                return

            try:
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(evaluation_counts):
                    selected_cid = evaluation_counts[selected_index].cid
                    consultant = session.query(Consultant).filter_by(cid=selected_cid).first()
                    consultant_name = consultant.fullname if consultant else "알 수 없음"

                    # 해당 컨설턴트에 대한 평가 목록 불러오기
                    evaluations = session.query(ConsultantEvaluation).filter_by(cid=selected_cid).all()
                    print(f"\n***** {consultant_name}(ID: {selected_cid})의 평가 목록 *****\n")
                    for idx, ev in enumerate(evaluations, start=1):
                        print(f"{idx}. {ev.evaluation_text}")

                    # 평가 관리(삭제 등)를 위한 옵션
                    while True:
                        action = input("평가 관리 옵션: 1: 평가 삭제, 0: 종료 >> ")
                        if action == '1':
                            del_choice = input("삭제할 평가 번호를 입력하세요 (0 입력 시 취소): ")
                            if del_choice == '0':
                                continue
                            try:
                                del_index = int(del_choice) - 1
                                if 0 <= del_index < len(evaluations):
                                    selected_eval = evaluations[del_index]
                                    confirm = input(f"'{selected_eval.evaluation_text}' 평가를 삭제하시겠습니까? (y/n): ").lower()
                                    if confirm == 'y':
                                        session.delete(selected_eval)
                                        session.commit()
                                        # 다시 평가목록 불러오기
                                        evaluations = session.query(ConsultantEvaluation).filter_by(cid=selected_cid).all()
                                        print("평가가 삭제되었습니다.")
                                    else:
                                        print("삭제가 취소되었습니다.")
                                else:
                                    print("잘못된 번호입니다.")
                            except ValueError:
                                print("유효한 번호를 입력하세요.")
                        elif action == '0':
                            print("평가 관리 종료.")
                            break
                        else:
                            print("잘못된 입력입니다.")
                else:
                    print("잘못된 번호입니다.")
            except ValueError:
                print("유효한 번호를 입력하세요.")
        except Exception as e:
            session.rollback()
            print(f"평가 관리 중 오류 발생: {e}")
        finally:
            session.close()
