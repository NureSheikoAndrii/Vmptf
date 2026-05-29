from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date, datetime
import warnings
from sqlalchemy.exc import SAWarning

# Ігноруємо попередження (для чистоти консолі)
warnings.filterwarnings('ignore', category=SAWarning)

Base = declarative_base()


# ---------- Моделі ----------
class Hotel(Base):
    __tablename__ = 'hotels'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String)
    rooms = relationship('Room', back_populates='hotel')


class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)


class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    room_number = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    price_per_night = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    hotel = relationship('Hotel', back_populates='rooms')
    bookings = relationship('Booking', back_populates='room')


class Service(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)


class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    status = Column(String, default='active')
    room = relationship('Room', back_populates='bookings')
    client = relationship('Client')


# ---------- Підключення до БД ----------
engine = create_engine('sqlite:///hotel_booking.db')
Base.metadata.create_all(engine)  # створить таблиці, якщо їх немає
Session = sessionmaker(bind=engine)
session = Session()


# ---------- Функції для консолі ----------
def show_available_rooms():
    """Показати всі доступні кімнати"""
    rooms = session.query(Room).filter(Room.is_available == True).all()
    if not rooms:
        print("\n❌ Немає доступних кімнат.")
        return

    print("\n" + "=" * 60)
    print("🏨 ДОСТУПНІ КІМНАТИ:")
    print("=" * 60)
    for room in rooms:
        hotel_name = room.hotel.name if room.hotel else "Невідомо"
        print(f"ID: {room.id} | Готель: {hotel_name} | Номер: {room.room_number} | "
              f"Місць: {room.capacity} | Ціна: {room.price_per_night} грн/ніч")
    print("=" * 60)


def show_all_bookings():
    """Показати всі активні бронювання"""
    bookings = session.query(Booking).filter(Booking.status == 'active').all()
    if not bookings:
        print("\n❌ Немає активних бронювань.")
        return

    print("\n" + "=" * 70)
    print("📋 ВСІ АКТИВНІ БРОНЮВАННЯ:")
    print("=" * 70)
    for booking in bookings:
        room = booking.room
        client = booking.client
        print(f"ID бронювання: {booking.id} | Клієнт: {client.full_name} | "
              f"Кімната: {room.room_number} | Заїзд: {booking.check_in} | "
              f"Виїзд: {booking.check_out}")
    print("=" * 70)


def add_booking_console():
    """Додати бронювання через консоль"""
    print("\n" + "=" * 50)
    print("➕ ДОДАТИ НОВЕ БРОНЮВАННЯ")
    print("=" * 50)

    # Показати доступні кімнати
    show_available_rooms()

    if session.query(Room).filter(Room.is_available == True).count() == 0:
        return

    # Введення даних
    try:
        room_id = int(input("\nВведіть ID кімнати: "))
        room = session.get(Room, room_id)

        if not room or not room.is_available:
            print("❌ Кімната не доступна!")
            return

        # Перевірка чи існує клієнт
        print("\nКлієнти в системі:")
        clients = session.query(Client).all()
        if not clients:
            print("❌ Немає клієнтів. Спочатку додайте клієнта через DB Browser.")
            return

        for client in clients:
            print(f"ID: {client.id} | Ім'я: {client.full_name} | Email: {client.email}")

        client_id = int(input("\nВведіть ID клієнта: "))
        client = session.get(Client, client_id)

        if not client:
            print("❌ Клієнта не знайдено!")
            return

        # Введення дат
        check_in_str = input("Дата заїзду (РРРР-ММ-ДД): ")
        check_out_str = input("Дата виїзду (РРРР-ММ-ДД): ")

        check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()

        if check_in >= check_out:
            print("❌ Дата виїзду має бути пізнішою за дату заїзду!")
            return

        # Створення бронювання
        booking = Booking(
            room_id=room_id,
            client_id=client_id,
            check_in=check_in,
            check_out=check_out
        )
        room.is_available = False
        session.add(booking)
        session.commit()

        nights = (check_out - check_in).days
        total_price = nights * room.price_per_night

        print(f"\n✅ Бронювання успішно створено! ID: {booking.id}")
        print(f"   Кімната: {room.room_number} | {nights} ночей | Всього: {total_price} грн")

    except ValueError:
        print("❌ Помилка введення! Перевірте формат даних.")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        session.rollback()


def cancel_booking_console():
    """Скасувати бронювання через консоль"""
    print("\n" + "=" * 50)
    print("❌ СКАСУВАТИ БРОНЮВАННЯ")
    print("=" * 50)

    # Показати всі бронювання
    show_all_bookings()

    try:
        booking_id = int(input("\nВведіть ID бронювання для скасування: "))
        booking = session.get(Booking, booking_id)

        if not booking or booking.status != 'active':
            print("❌ Бронювання не знайдено або вже скасоване!")
            return

        # Підтвердження
        confirm = input(f"Скасувати бронювання #{booking_id}? (так/ні): ").lower()
        if confirm == 'так':
            booking.status = 'cancelled'
            booking.room.is_available = True
            session.commit()
            print(f"✅ Бронювання #{booking_id} скасовано!")
        else:
            print("❌ Скасування відмінено.")

    except ValueError:
        print("❌ Помилка! Введіть число.")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        session.rollback()


# ---------- ГОЛОВНЕ МЕНЮ ----------
def main_menu():
    """Головне меню програми"""
    while True:
        print("\n" + "=" * 50)
        print("🏨 СИСТЕМА БРОНЮВАННЯ ГОТЕЛІВ")
        print("=" * 50)
        print("1️⃣  Показати доступні кімнати")
        print("2️⃣  Показати всі бронювання")
        print("3️⃣  Додати бронювання")
        print("4️⃣  Скасувати бронювання")
        print("5️⃣  Вийти")
        print("=" * 50)

        choice = input("Оберіть опцію (1-5): ")

        if choice == '1':
            show_available_rooms()
        elif choice == '2':
            show_all_bookings()
        elif choice == '3':
            add_booking_console()
        elif choice == '4':
            cancel_booking_console()
        elif choice == '5':
            print("\n👋 До побачення!")
            session.close()
            break
        else:
            print("❌ Невірний вибір! Спробуйте ще раз.")


# ---------- ЗАПУСК ----------
if __name__ == '__main__':
    # Перевірка чи є дані в БД
    if session.query(Client).count() == 0:
        print("\n⚠️  УВАГА: У базі даних немає клієнтів!")
        print("Додайте клієнтів через DB Browser SQLite в таблицю 'clients'")
        print("Або додайте тестових клієнтів вручну.\n")

    main_menu()