import asyncio
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import StateFilter, CommandStart, ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.types import Message, ChatMemberUpdated
from sqlalchemy import select, insert, update, delete

from bot import bot
from config import ADMIN_IDS
from models import User, Session
from spread import get_sheet

router =Router()

class FSMFillForm(StatesGroup):
    fill_name = State()
    fill_contract = State()
    fill_tube = State()
    fill_vk = State()
    fill_video = State()


async def scheduler(time):
    while True:
        await asyncio.sleep(10)
        print(datetime.now())
        try:
            async with Session() as session:
                query = select(User)
                res = await session.execute(query)
            sheet = await get_sheet()
            sheet.clear()
            title = ['id', 'Статус', 'user_id', 'username', 'first_name', 'last_name',
                          'Время входа в бота', 'ФИО', 'Время ввода ФИО', 'Договор', 'Время Договора',
                          'Ник Youtube', 'Время Yotube', 'Ник ВК', 'Время ВК', 'Видео', 'Время Видео',
                          datetime.now().strftime('%Y-%m-%d   %H:%M:%S')]
            user_list = []
            for row in res.scalars():
                time_name = None
                time_contract = None
                time_tube = None
                time_vk = None
                time_video = None
                if row.time_name:
                    time_name = row.time_name.strftime('%Y-%m-%d   %H:%M:%S')
                if row.time_contract:
                    time_contract = row.time_contract.strftime('%Y-%m-%d   %H:%M:%S')
                if row.time_tube:
                    time_tube = row.time_tube.strftime('%Y-%m-%d   %H:%M:%S')
                if row.time_vk:
                    time_vk = row.time_vk.strftime('%Y-%m-%d   %H:%M:%S')
                if row.time_video:
                    time_video = row.time_video.strftime('%Y-%m-%d   %H:%M:%S')

                user_list.append([row.id, row.state, row.user_id, row.username, row.first_name, row.last_name,
                                  row.time_start.strftime('%Y-%m-%d   %H:%M:%S'), row.name, time_name, row.contract,
                                  time_contract, row.tube_nick, time_tube, row.vk_nick, time_vk, row.video, time_video])
                user_list.sort()
            sheet.append_rows([title] + user_list)
        except Exception as e:
            await bot.send_message(1012882762, str(e))
        await asyncio.sleep(time)


@router.message(CommandStart(), StateFilter(default_state), ~F.from_user.id.in_(ADMIN_IDS))
async def process_start(msg: Message, state: FSMContext):
    async with (Session() as session):
        query = select(User.user_id).where(User.user_id == str(msg.from_user.id))
        results = await session.execute(query)
        if not results.scalar():
            stmt = insert(User).values(
                user_id=str(msg.from_user.id),
                username=msg.from_user.username,
                first_name=msg.from_user.first_name,
                last_name=msg.from_user.last_name,
                state="Активен",
                time_start=datetime.now()
            )
            await session.execute(stmt)
            await session.commit()
            await msg.answer(text="Привет! Это компания Старт!\n\nПожалуйста, напишите Ваше ФИО.")
            await state.set_state(FSMFillForm.fill_name)
        else:
            await msg.answer(text="Вы уже участвуете в розыгрыше. Ждите результатов - мы сообщим.")


@router.message(
    StateFilter(FSMFillForm.fill_name),
    lambda m: m.text.replace(' ', '').isalpha() is True)
async def process_name_sent(msg: Message, state: FSMContext):
    async with (Session() as session):
        stmt = update(User).where(User.user_id == str(msg.from_user.id)).values(name=msg.text,
                                                                                time_name=datetime.now())
        await session.execute(stmt)
        await session.commit()
    await msg.answer(text='Спасибо!\n\nТеперь, пожалуйста, укажите номер вашего договора.')
    await state.set_state(FSMFillForm.fill_contract)


@router.message(StateFilter(FSMFillForm.fill_name))
async def process_name_wrong(msg: Message):
    await msg.answer(text='Что-то пошло не так\n'
                              'ФИО должно состоять из букв\n'
                              'Пожалуйста введите повторно ФИО')


@router.message(
    StateFilter(FSMFillForm.fill_contract),
    lambda m: m.text.replace(' ', '').isdigit() is True)
async def process_contract_sent(msg: Message, state: FSMContext):
    async with (Session() as session):
        stmt = update(User).where(User.user_id == str(msg.from_user.id)).values(contract=msg.text,
                                                                                time_contract=datetime.now())
        await session.execute(stmt)
        await session.commit()
    await msg.answer(text='Спасибо!\n\nТеперь, пожалуйста, укажите ваш ник на YouTube.')
    await state.set_state(FSMFillForm.fill_tube)


@router.message(StateFilter(FSMFillForm.fill_contract))
async def process_contract_wrong(msg: Message):
    await msg.answer(text='Что-то пошло не так\n'
                              'Номер договора должен состоять из цифр\n'
                              'Пожалуйста введите повторно номер договора')


@router.message(StateFilter(FSMFillForm.fill_tube), F.text)
async def process_youtube_sent(msg: Message, state: FSMContext):
    async with (Session() as session):
        stmt = update(User).where(User.user_id == str(msg.from_user.id)).values(tube_nick=msg.text,
                                                                                time_tube=datetime.now())
        await session.execute(stmt)
        await session.commit()
    await msg.answer(text='Спасибо!\n\nТеперь, пожалуйста, укажите ваш ник в ВКонтакте.')
    await state.set_state(FSMFillForm.fill_vk)


@router.message(StateFilter(FSMFillForm.fill_tube))
async def process_youtube_wrong(msg: Message):
    await msg.answer(text='Что-то пошло не так\n'
                          'Напишите ник в текстовом сообщении')


@router.message(StateFilter(FSMFillForm.fill_vk), F.text)
async def process_vk_sent(msg: Message, state: FSMContext):
    async with (Session() as session):
        stmt = update(User).where(User.user_id == str(msg.from_user.id)).values(vk_nick=msg.text,
                                                                                time_vk=datetime.now())
        await session.execute(stmt)
        await session.commit()
    await msg.answer(text='Отлично!\n\n Пожалуйста, загрузите видео.')
    await state.set_state(FSMFillForm.fill_video)


@router.message(StateFilter(FSMFillForm.fill_vk))
async def process_vk_wrong(msg: Message):
    await msg.answer(text='Что-то пошло не так\n'
                          'Напишите ник в текстовом сообщении')


@router.message(StateFilter(FSMFillForm.fill_video), F.video)
async def process_video_sent(msg: Message, state: FSMContext):
    async with (Session() as session):
        stmt = update(User).where(User.user_id == str(msg.from_user.id)).values(video=msg.video.file_id,
                                                                                time_video=datetime.now())
        await session.execute(stmt)
        await session.commit()
        query = select(User.id).where(User.user_id == str(msg.from_user.id))
        res = await session.execute(query)
    await msg.answer(text=f'Спасибо за предоставленные ответы!\nВаш уникальный номер - {res.first()[0]}!\n'
                          f'Желаю удачи в розыгрыше!')
    await state.set_state(default_state)


@router.message(StateFilter(FSMFillForm.fill_video))
async def process_video_file(msg: Message):
    await msg.answer(text='Что-то пошло не так\n'
                              'Пришлите пжл сообщение в формате видео')


@router.message(CommandStart(), F.from_user.id.in_(ADMIN_IDS))
async def process_start_admin(mes: Message):
    await mes.answer(text="Вы админ бота, для загрузки видео клиента введите пжл уникальный номер юзера.\n\n"
                          "Данные юзеров доступны <a href='https://docs.google.com/spreadsheets/d/"
                          "1EJpnscQbDO7_zaWeFcj3bKhntON4W0uK3H5cGo9QTYI/edit#gid=0'>по ссылке</a>",
                     disable_web_page_preview=True,
                     parse_mode="HTML")


@router.message(F.from_user.id == 1012882762, F.text == "testdel")
async def process_delete(mes: Message):
    try:
        async with Session() as session:
            stmt = delete(User).where(User.user_id == '7490319693')
            await session.execute(stmt)
            await session.commit()
    except Exception as e:
        await bot.send_message(1012882762, str(e))


@router.message(F.from_user.id.in_(ADMIN_IDS),
                lambda m: m.text.isdigit() is True)
async def process_admin(msg: Message):
    async with (Session() as session):
        query = select(User.video).where(User.id == int(msg.text))
        res = await session.execute(query)
        try:
            video = res.first()[0]
            if video:
                await msg.answer_video(video=video)
            else:
                await msg.answer(text="Видео не загружено для данного пользователя")
        except TypeError:
            await msg.answer(text="Пользователя с таким id нет в базе")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    async with (Session() as session):
        stmt = update(User).where(User.user_id == str(event.from_user.id)).values(state="Заблокировал бота")
        await session.execute(stmt)
        await session.commit()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    async with (Session() as session):
        stmt = update(User).where(User.user_id == str(event.from_user.id)).values(state="Активен")
        await session.execute(stmt)
        await session.commit()


@router.message(~F.from_user.id.in_(ADMIN_IDS), StateFilter(default_state))
async def process_forward_msg(mes: Message):
    for chat_id in ADMIN_IDS:
        await bot.forward_message(chat_id=chat_id, from_chat_id=mes.chat.id, message_id=mes.message_id)


