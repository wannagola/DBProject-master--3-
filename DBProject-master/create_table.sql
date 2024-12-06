-- 기존 테이블 삭제
DROP TABLE IF EXISTS tax_bracket CASCADE;
DROP TABLE IF EXISTS customer_family CASCADE;
DROP TABLE IF EXISTS consultant_respond CASCADE;
DROP TABLE IF EXISTS consultant_explain CASCADE;
DROP TABLE IF EXISTS ban_list CASCADE;
DROP TABLE IF EXISTS customer_request CASCADE;
DROP TABLE IF EXISTS consultant_evaluation CASCADE;
DROP TABLE IF EXISTS customer_income_list CASCADE;
DROP TABLE IF EXISTS consultant CASCADE;
DROP TABLE IF EXISTS customer CASCADE;
DROP TABLE IF EXISTS manager CASCADE;

-- 테이블 생성

CREATE TABLE manager (
    MID VARCHAR(15) PRIMARY KEY,
    fullname VARCHAR(5) NOT NULL,
    section VARCHAR(15) NOT NULL
);

CREATE TABLE customer (
    ID VARCHAR(15) PRIMARY KEY,
    password VARCHAR(15) NOT NULL,
    telephone NUMERIC(11,0) NOT NULL,
    email VARCHAR(50) NOT NULL,
    fullname VARCHAR(5) NOT NULL,
    expected_tax NUMERIC(10,0),
    verification VARCHAR(10) -- customer.py 내 verification 컬럼 반영하기
);

CREATE TABLE consultant (
    CID VARCHAR(15) PRIMARY KEY,
    password VARCHAR(15) NOT NULL,
    telephone NUMERIC(11,0) NOT NULL,
    email VARCHAR(50) NOT NULL,
    fullname VARCHAR(5) NOT NULL,
    certification VARCHAR(10) NOT NULL,
    certification_status VARCHAR(10) DEFAULT 'pending' -- 매니저에 의한 인증 상태 관리 컬럼 추가
);

CREATE TABLE customer_income_list (
    ID VARCHAR(15) PRIMARY KEY,
    interest NUMERIC(10,0),
    dividend NUMERIC(10,0),
    business NUMERIC(10,0),
    earned NUMERIC(10,0),
    pension NUMERIC(10,0),
    other NUMERIC(10,0),
    FOREIGN KEY (ID) REFERENCES customer(ID) ON DELETE CASCADE
);

CREATE TABLE consultant_evaluation (
    ID VARCHAR(15) NOT NULL,
    CID VARCHAR(15) NOT NULL,
    evaluation_text VARCHAR(500),
    PRIMARY KEY (ID, CID),
    FOREIGN KEY (ID) REFERENCES customer(ID) ON DELETE CASCADE,
    FOREIGN KEY (CID) REFERENCES consultant(CID) ON DELETE CASCADE
);

CREATE TABLE customer_request (
    ID VARCHAR(15) NOT NULL,
    title VARCHAR(100) NOT NULL,
    request_text VARCHAR(500),
    PRIMARY KEY (ID, title),
    FOREIGN KEY (ID) REFERENCES customer(ID) ON DELETE CASCADE
);

CREATE TABLE ban_list (
    ID VARCHAR(15) NOT NULL,
    CID VARCHAR(15) NOT NULL,
    PRIMARY KEY (ID, CID),
    FOREIGN KEY (ID) REFERENCES customer(ID) ON DELETE CASCADE,
    FOREIGN KEY (CID) REFERENCES consultant(CID) ON DELETE CASCADE
);

CREATE TABLE consultant_explain (
    CID VARCHAR(15) PRIMARY KEY,
    explain_text VARCHAR(500),
    FOREIGN KEY (CID) REFERENCES consultant(CID) ON DELETE CASCADE
);

CREATE TABLE consultant_respond (
    ID VARCHAR(15) NOT NULL,
    title VARCHAR(100) NOT NULL,
    CID VARCHAR(15) NOT NULL,
    respond_text VARCHAR(500),
    PRIMARY KEY (ID, title, CID),
    FOREIGN KEY (ID, title) REFERENCES customer_request(ID, title) ON DELETE CASCADE,
    FOREIGN KEY (CID) REFERENCES consultant(CID) ON DELETE CASCADE
);

CREATE TABLE customer_family (
    ID VARCHAR(15) NOT NULL,
    family_user_name VARCHAR(15) NOT NULL,
    deduction NUMERIC(9,0),
    verification VARCHAR(10) UNIQUE NOT NULL,
    PRIMARY KEY (ID, family_user_name),
    FOREIGN KEY (ID) REFERENCES customer(ID) ON DELETE CASCADE
);

CREATE TABLE tax_bracket (
    id varchar(2) not null,
    upper_limit NUMERIC(15,2) NOT NULL,
    rate NUMERIC(5,4) NOT NULL,
    deduction NUMERIC(15,2) NOT NULL,
    PRIMARY KEY (id)
);
