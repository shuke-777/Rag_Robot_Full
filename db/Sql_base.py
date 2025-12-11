import asyncio

from sqlalchemy.orm import (sessionmaker, declarative_base, Mapped, MappedColumn,
                            relationship,)
from sqlalchemy import ForeignKey, String, create_engine,select,Text
from typing import Optional, List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# ==================== Base ====================
base = declarative_base()

# ==================== 模型定义 ====================
class Userinfo(base):
    __tablename__ = 'rag_base'
    id: Mapped[int] = MappedColumn(primary_key=True)
    name: Mapped[str] = MappedColumn(String(30))
    full_name: Mapped[Optional[str]] = MappedColumn(String(255), nullable=True)
    # 这里用List[MyAddress]是一对多
    add_relations: Mapped[List['MyAddress']] = relationship('MyAddress',
                                                             back_populates='user',
                                                             cascade='all,delete-orphan')

    # 这里是返回__repr__
    def __repr__(self):
        return f'Userinfo(id ={self.id !r},name = {self.name !r},full_name = {self.full_name !r})'


class MyAddress(base):
    __tablename__ = 'addresses'
    address_id: Mapped[int] = MappedColumn(primary_key=True)
    email_addresses: Mapped[str] = MappedColumn(String(50))
    user_id: Mapped[int] = MappedColumn(ForeignKey('rag_base.id'))
    # 这里是多对一
    user: Mapped['Userinfo'] = relationship('Userinfo', back_populates='add_relations')

    def __repr__(self):
        return f'MyAddress(address_id = {self.address_id !r},email_addresses = {self.email_addresses !r})'
class SessionTable(base):
    __tablename__ = 'session_table_new'
    id:Mapped[int] = MappedColumn(primary_key=True)
    session_id:Mapped[str] = MappedColumn(String(255),unique=True)
    message_relation:Mapped[List['MessagesTableNew']] = relationship(
        'MessagesTableNew',
        back_populates='session_relation',
        cascade='all,delete-orphan'
    )
class MessagesTableNew(base):
    __tablename__ = 'message_table_new'
    id:Mapped[int] = MappedColumn(primary_key=True)
    #这里就是代表着session_id多对一，这里的session_id=session_table_new.id
    session_id :Mapped[int] = MappedColumn(ForeignKey('session_table_new.id'))
    content:Mapped[str] = MappedColumn(Text)
    role:Mapped[str] = MappedColumn(String(255))
    session_relation:Mapped['SessionTable'] = relationship(
        'SessionTable',
        back_populates='message_relation'
    )

# ==================== 数据库配置 ====================
user_name = 'shuke'
password = '123456'
host_name = 'localhost'
database_name = 'sk_db'

# 同步数据库URL
db_url = f'mysql+pymysql://{user_name}:{password}@{host_name}/{database_name}?charset=utf8mb4'
#print(db_url)

# 创建async_db_url
db_url_async = f'mysql+aiomysql://{user_name}:{password}@{host_name}/{database_name}?charset=utf8mb4'

# echo=True表示打印sql语句
engine1 = create_engine(db_url)

# 创建async engine
engine_async = create_async_engine(db_url_async, echo=True)

# base.metadata.create_all(engine1)
session1 = sessionmaker(bind=engine1)

# async_session
async_session = async_sessionmaker(bind=engine_async, class_=AsyncSession)


# ==================== 异步函数 ====================
async def async_create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
        print('创建成功')
    await engine.dispose()

# ==================== 异步函数query ====================
async def async_query_example(engine):
    async with async_session() as session:
        query = select(Userinfo).filter(Userinfo.name == 'sandy')
        result = await session.execute(query)
        u1 = result.scalars().all()
        for u in u1:
            print(u)
    await engine.dispose()

# ==================== 同步函数 ====================
def main():
    with session1() as session:
        spongebob = Userinfo(
            name='spongebob',
            add_relations=[MyAddress(email_addresses='spongebob@sqlalchemy.org')]
        )
        sandy = Userinfo(
            name='sandy',
            add_relations=[MyAddress(email_addresses='123@qq.com'),
                           MyAddress(email_addresses='456@qq.com')]
        )
        patrick = Userinfo(name='patrick',
                           full_name='patrick_dawn')
        session.add_all([spongebob, sandy, patrick])
        session.commit()

# ==================== 主程序 ====================
if __name__ == '__main__':
    # print(session1().query(Userinfo).first())
   # u1 = session1().query(Userinfo).filter(Userinfo.name == 'sandy').all()
    # for u in u1:
    #     #print(u)
    #     for addr in u.add_relations:
    # print(addr)

    # a1 = session1().query(MyAddress).filter(MyAddress.email_addresses == '123@qq.com').all()
    # for a in a1:
    #     print(a.user)

    # async_create_tables
    asyncio.run(async_create_tables(engine_async))
    #async_query
   # asyncio.run(async_query_example(engine_async))