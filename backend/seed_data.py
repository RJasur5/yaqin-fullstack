"""
Seed data script — creates categories, subcategories, and demo masters.
Run: python seed_data.py
"""

from database import engine, SessionLocal, Base
from models import User, Category, Subcategory, MasterProfile, Review
from passlib.context import CryptContext
import random

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # ==================== CATEGORIES & SUBCATEGORIES ====================
    categories_data = [
        {
            "name_ru": "Строительство", "name_uz": "Qurilish", "icon": "construction", "color": "#FF6B35",
            "subs": [("Слесарь", "Chilangar"), ("Сантехник", "Santexnik"), ("Электрик", "Elektrik"), ("Маляр", "Bo'yoqchi"), ("Плотник", "Duradgor"), ("Сварщик", "Payvandchi"), ("Каменщик", "Toshchi"), ("Штукатур", "Suvoqchi"), ("Монтажник", "Montajchi"), ("Кровельщик", "Tom yopuvchi"), ("Бетонщик", "Betonchi"), ("Арматурщик", "Armaturachi"), ("Стекольщик", "Oynachi"), ("Изолировщик", "Izolyatsiyachi"), ("Фасадчик", "Fasadchi"), ("Прораб", "Prorab")]
        },
        {
            "name_ru": "Медицина", "name_uz": "Tibbiyot", "icon": "medical_services", "color": "#E63946",
            "subs": [("Гинеколог", "Ginekolog"), ("Ортопед", "Ortoped"), ("Терапевт", "Terapevt"), ("Стоматолог", "Stomatolog"), ("Кардиолог", "Kardiolog"), ("Невролог", "Nevrolog"), ("ЛОР", "LOR"), ("Дерматолог", "Dermatolog"), ("Хирург", "Xirurg"), ("Офтальмолог", "Oftalmolog"), ("Педиатр", "Pediatr"), ("Уролог", "Urolog"), ("Эндокринолог", "Endokrinolog"), ("Психиатр", "Psixiatr"), ("Онколог", "Onkolog"), ("Аллерголог", "Allergolog")]
        },
        {
            "name_ru": "Образование", "name_uz": "Ta'lim", "icon": "school", "color": "#457B9D",
            "subs": [("Учитель истории", "Tarix o'qituvchisi"), ("Учитель русского", "Rus tili o'qituvchisi"), ("Учитель математики", "Matematika o'qituvchisi"), ("Учитель английского", "Ingliz tili o'qituvchisi"), ("Учитель физики", "Fizika o'qituvchisi"), ("Учитель химии", "Kimyo o'qituvchisi"), ("Репетитор", "Repetitor"), ("Логопед", "Logoped"), ("Тренер", "Trener"), ("Бизнес-тренер", "Biznes-trener"), ("Психолог", "Psixolog"), ("Куратор", "Kurator"), ("Методист", "Metodist"), ("Преподаватель ВУЗа", "OTM o'qituvchisi"), ("Астроном", "Astronom")]
        },
        {
            "name_ru": "Авто", "name_uz": "Avto", "icon": "directions_car", "color": "#2D6A4F",
            "subs": [("Автомеханик", "Avtomexanik"), ("Автоэлектрик", "Avtoelektrik"), ("Кузовщик", "Kuzovchi"), ("Шиномонтаж", "Shinomontaj"), ("Покраска авто", "Avto bo'yash"), ("Моторист", "Motorist"), ("Диагност", "Diagnost"), ("Автомойщик", "Avtoyuvuvchi"), ("Тюнинг", "Tyuning"), ("Ремонт ходовой", "Xodovoy ta'miri"), ("Тонировщик", "Tonirovka ustasi"), ("Установка ГБО", "Gaz balon o'rnatish"), ("Автокондиционеры", "Avtokonditsionerlar")]
        },
        {
            "name_ru": "IT и техника", "name_uz": "IT va texnika", "icon": "computer", "color": "#7209B7",
            "subs": [("Программист", "Dasturchi"), ("Веб-разработчик", "Veb-dasturchi"), ("Ремонт компьютеров", "Kompyuter ta'mirlash"), ("Ремонт телефонов", "Telefon ta'mirlash"), ("Сисадмин", "Tizim administratori"), ("QA тестировщик", "QA testlovchi"), ("Аналитик", "Analitik"), ("DevOps", "DevOps"), ("Дизайнер UI/UX", "UI/UX dizayner"), ("Ремонт бытовой техники", "Maishiy texnika ta'mirlash"), ("Установка камер", "Kamera o'rnatish"), ("Мастер по принтерам", "Printer ustasi"), ("Настройка сетей", "Tarmoq sozlash"), ("Data Scientist", "Data Scientist"), ("Ремонт ТВ", "TV ta'mirlash")]
        },
        {
            "name_ru": "Красота", "name_uz": "Go'zallik", "icon": "spa", "color": "#F72585",
            "subs": [("Парикмахер", "Sartarosh"), ("Визажист", "Vizajist"), ("Мастер маникюра", "Manikur ustasi"), ("Косметолог", "Kosmetolog"), ("Массажист", "Massajist"), ("Барбер", "Barber"), ("Мастер педикюра", "Pedikyur ustasi"), ("Наращивание ресниц", "Kiprik ulash"), ("Шугаринг", "Shugaring"), ("Стилист", "Stilist"), ("Бровист", "Brovist"), ("Тату-мастер", "Tatu ustasi"), ("Пирсинг", "Pirsing"), ("Трихолог", "Trixolog"), ("Лазерная эпиляция", "Lazer epilyatsiyasi")]
        },
        {
            "name_ru": "Юриспруденция", "name_uz": "Huquqshunoslik", "icon": "gavel", "color": "#1D3557",
            "subs": [("Адвокат", "Advokat"), ("Нотариус", "Notarius"), ("Юрист по бизнесу", "Biznes yuristi"), ("Семейный юрист", "Oilaviy yurist"), ("Уголовный адвокат", "Jinoiy advokat"), ("Следователь", "Tergovchi"), ("Юрисконсульт", "Yuriskonsult"), ("Арбитр", "Hakam"), ("Медиатор", "Mediator"), ("Автоюрист", "Avtoyurist"), ("Корпоративный юрист", "Korporativ yurist"), ("Защита прав потребителей", "Iste'molchi huquqini himoya qilish"), ("Юрист по недвижимости", "Ko'chmas mulk yuristi"), ("Налоговый юрист", "Soliq yuristi")]
        },
        {
            "name_ru": "Перевозки", "name_uz": "Tashish", "icon": "local_shipping", "color": "#E76F51",
            "subs": [("Грузоперевозки", "Yuk tashish"), ("Переезд", "Ko'chish"), ("Курьер", "Kuryer"), ("Такси", "Taksi"), ("Трезвый водитель", "Sog'lom haydovchi"), ("Эвакуатор", "Evakuator"), ("Международник", "Xalqaro tashuvchi"), ("Доставка еды", "Ovqat yetkazish"), ("Логист", "Logist"), ("Водитель погрузчика", "Yuklagich haydovchisi"), ("Пассажирские перевозки", "Yo'lovchi tashish"), ("Аренда спецтехники", "Maxsus texnika ijarasi"), ("Экспедитор", "Ekspeditor"), ("АВИА доставка", "AVIA yetkazib berish")]
        },
        {
            "name_ru": "Клининг", "name_uz": "Tozalash", "icon": "cleaning_services", "color": "#4CC9F0",
            "subs": [("Уборка квартир", "Kvartira tozalash"), ("Химчистка", "Kimyoviy tozalash"), ("Мойка окон", "Deraza yuvish"), ("Уборка офисов", "Ofis tozalash"), ("Генеральная уборка", "Umumiy tozalash"), ("Уборка после ремонта", "Ta'mirdan keyingi tozalash"), ("Вывоз мусора", "Chiqindi olib ketish"), ("Дезинсекция", "Dezinseksiya"), ("Уборка территории", "Hududni tozalash"), ("Чистка ковров", "Gilam tozalash"), ("Мытье фасадов", "Fasad yuvish"), ("Уборка бассейнов", "Hovuz tozalash"), ("Глажка белья", "Kiyim dazmollash")]
        },
        {
            "name_ru": "Дизайн", "name_uz": "Dizayn", "icon": "palette", "color": "#FB8500",
            "subs": [("Дизайн интерьера", "Interyer dizayni"), ("Графический дизайн", "Grafik dizayn"), ("Ландшафтный дизайн", "Landshaft dizayni"), ("3D-визуализация", "3D-vizualizatsiya"), ("Архитектор", "Arxitektor"), ("Веб-дизайн", "Veb-dizayn"), ("Дизайн одежды", "Kiyim dizayni"), ("Промышленный дизайн", "Sanoat dizayni"), ("Аниматор", "Animator"), ("Иллюстратор", "Illyustrator"), ("Оформление праздников", "Bayramlarni bezatish"), ("Флорист", "Florist"), ("Дизайн упаковки", "Qadoq dizayni"), ("Дизайн мебели", "Mebel dizayni"), ("Брендинг", "Brending")]
        },
        {
            "name_ru": "Спорт и фитнес", "name_uz": "Sport va fitnes", "icon": "fitness_center", "color": "#7FB069",
            "subs": [("Фитнес-инструктор", "Fitnes instruktori"), ("Личный тренер", "Shaxsiy trener"), ("Йога", "Yoga"), ("Пилатес", "Pilates"), ("Тренер по плаванию", "Suzish treneri"), ("Тренер по боксу", "Boks treneri"), ("Хореограф", "Xoreograf"), ("Тренер по теннису", "Tennis treneri"), ("Мастер боевых искусств", "Jang san'atlar ustasi"), ("Тренер по гимнастике", "Gimnastika treneri"), ("Спортивный диетолог", "Sport diyetologi"), ("Тренер по футболу", "Futbol treneri"), ("Спортивный массаж", "Sport massaji"), ("Зумба", "Zumba"), ("Кроссфит", "Krossfit")]
        },
        {
            "name_ru": "Творчество", "name_uz": "Ijodkorlik", "icon": "color_lens", "color": "#F4A261",
            "subs": [("Художник", "Rassom"), ("Музыкант", "Musiqachi"), ("Певец", "Xonanda"), ("Актёр", "Aktyor"), ("Режиссёр", "Rejissyor"), ("Сценарист", "Ssenarist"), ("Писатель", "Yozuvchi"), ("Композитор", "Kompozitor"), ("Звукорежиссёр", "Ovoz rejissyori"), ("Танцор", "Raqqosa"), ("Скульптор", "Haykaltarosh"), ("Диджей", "Di-jey"), ("Ведущий мероприятий", "Tadbirlar boshlovchisi"), ("Клоун", "Masxaraboz"), ("Иллюзионист", "Illyuzionist")]
        },
        {
            "name_ru": "Рестораны и питание", "name_uz": "Restoran va oziq-ovqat", "icon": "restaurant", "color": "#E9C46A",
            "subs": [("Шеф-повар", "Oshpaz"), ("Су-шеф", "Su-shef"), ("Кондитер", "Qandolatchi"), ("Пекарь", "Novvoy"), ("Бармен", "Barmen"), ("Бариста", "Barista"), ("Официант", "Ofitsiant"), ("Мангальщик", "Mangalchi"), ("Пиццайоло", "Pitsayolo"), ("Сушист", "Sushist"), ("Менеджер ресторана", "Restoran menedjeri"), ("Кальянщик", "Kalyanchi"), ("Организатор банкетов", "Banketlar tashkilotchisi"), ("Технолог", "Texnolog"), ("Доставка еды", "Ovqat yetkazib beruvchi")]
        },
        {
            "name_ru": "Сельское хозяйство", "name_uz": "Qishloq xo'jaligi", "icon": "agriculture", "color": "#2A9D8F",
            "subs": [("Агроном", "Agronom"), ("Ветеринар", "Veterinar"), ("Фермер", "Fermer"), ("Садовник", "Bog'bon"), ("Животновод", "Chorvador"), ("Тепличник", "Issiqxonachi"), ("Тракторист", "Traktorchi"), ("Пчеловод", "Asalarichi"), ("Птицевод", "Parrandachi"), ("Рыбовод", "Baliqchi"), ("Сборщик урожая", "Hosil yig'uvchi"), ("Механизатор", "Mexanizator"), ("Лесник", "O'rmonchi"), ("Ландшафтный озеленитель", "Landshaft yashillashtiruvchisi"), ("Фитопатолог", "Fitopatolog")]
        },
        {
            "name_ru": "Недвижимость", "name_uz": "Ko'chmas mulk", "icon": "apartment", "color": "#264653",
            "subs": [("Риэлтор", "Rieltor"), ("Оценщик имущества", "Mulk baholovchi"), ("Брокер", "Broker"), ("Ипотечный консультант", "Ipoteka konsultanti"), ("Менеджер по аренде", "Ijara menedjeri"), ("Агент по продажам", "Sotish agenti"), ("Специалист по земле", "Yer mutaxassisi"), ("Девелопер", "Dasturchi"), ("Инвестор", "Investor"), ("Сметчик", "Smetachi"), ("Специалист по коммерческой недвижимости", "Tijorat ko'chmas mulk mutaxassisi"), ("Кадастровый инженер", "Kadasr muhandisi"), ("Управляющий недвижимостью", "Mulk boshqaruvchisi"), ("Нотариус по недвижимости", "Mulk notariusi")]
        },
        {
            "name_ru": "Медиа и маркетинг", "name_uz": "Media va marketing", "icon": "campaign", "color": "#8AB17D",
            "subs": [("SMM-специалист", "SMM-mutaxassisi"), ("Таргетолог", "Targetolog"), ("Копирайтер", "Kopirayter"), ("SEO-оптимизатор", "SEO-optimizator"), ("Видеомонтажёр", "Videomontajchi"), ("Фотограф", "Fotograf"), ("Маркетолог", "Marketolog"), ("Контент-менеджер", "Kontent-menedjer"), ("Блогер", "Blogger"), ("Пиар-менеджер", "PR-menedjer"), ("Криэйтор", "Kriyeytor"), ("Модель", "Model"), ("Спортивный обозреватель", "Sport sharhlovchisi"), ("Редактор", "Muharrir"), ("Диктор", "Suxandon")]
        },
        {
            "name_ru": "Туризм и отдых", "name_uz": "Turizm va dam olish", "icon": "flight_takeoff", "color": "#219EBC",
            "subs": [("Турагент", "Turagent"), ("Экскурсовод", "Ekskursovod"), ("Переводчик", "Tarjimon"), ("Отельный менеджер", "Mehmonxona menedjeri"), ("Организатор туров", "Turlar tashkilotchisi"), ("Гид", "Gid"), ("Аниматор (отели)", "Animator (mehmonxonalar)"), ("Менеджер визового центра", "Viza markazi menedjeri"), ("Стюард/Стюардесса", "Bortkuzatuvchi"), ("Менеджер по бронированию", "Bron qilish menedjeri"), ("Трансфер", "Transfer"), ("Инструктор по туризму", "Turizm instruktori"), ("Горный гид", "Tog' gidi"), ("Менеджер по мероприятиям", "Tadbirlar menedjeri"), ("Организатор кемпинга", "Kemping tashkilotchisi")]
        },
        {
            "name_ru": "Домашний персонал", "name_uz": "Uy xodimlari", "icon": "house_siding", "color": "#FFB703",
            "subs": [("Няня", "Enaga"), ("Сиделка", "Kutuvchi"), ("Домработница", "Uy xizmatchisi"), ("Повар в семью", "Oila oshpazi"), ("Помощник садовника", "Bog'bonga yordamchi"), ("Водитель для семьи", "Oila haydovchisi"), ("Гувернантка", "Guvernantka"), ("Дворецкий", "Dvoretskiy"), ("Охранник", "Qorovul"), ("Помощник по хозяйству", "Xo'jalik yordamchisi"), ("Экономка", "Tejamkor"), ("Репетитор для детей", "Bolalar uchun repetitor"), ("Специалист по уходу за питомцами", "Uy hayvonlarini parvarishlash mutaxassisi"), ("Уборщица", "Farrosh")]
        },
    ]

    all_subcategories = []
    for idx, cat_data in enumerate(categories_data):
        cat = Category(
            name_ru=cat_data["name_ru"],
            name_uz=cat_data["name_uz"],
            icon=cat_data["icon"],
            color=cat_data["color"],
            order_index=idx,
        )
        db.add(cat)
        db.flush()

        for sub_name_ru, sub_name_uz in cat_data["subs"]:
            sub = Subcategory(
                category_id=cat.id,
                name_ru=sub_name_ru,
                name_uz=sub_name_uz,
            )
            db.add(sub)
            db.flush()
            all_subcategories.append(sub)

    # ==================== DEMO USERS & MASTERS ====================
    cities = [
        "Toshkent", "Samarqand", "Buxoro", "Andijon", "Namangan", "Farg'ona", 
        "Nukus", "Navoiy", "Urganch", "Qarshi", "Jizzax", "Termiz", "Xiva", "Guliston"
    ]

    demo_names = [
        "Алишер Каримов", "Бахтиёр Усманов", "Шахзод Рахимов", "Дилшод Мирзаев",
        "Нодир Хасанов", "Озод Тошматов", "Жавохир Исмоилов", "Сардор Абдуллаев",
        "Ботир Турсунов", "Фарход Юлдашев", "Акмал Нурматов", "Рустам Азимов",
        "Тимур Шарипов", "Ильхом Рашидов", "Мансур Закиров", "Улугбек Салимов",
        "Лола Ахмедова", "Гулнора Каримова", "Дилнавоз Мирзаева", "Зарина Файзуллаева",
        "Малика Хамидова", "Наргиза Юсупова", "Севара Хошимова", "Мадина Рахматуллаева",
    ]

    demo_descriptions_ru = [
        "Опытный специалист с многолетним стажем. Работаю качественно и в срок.",
        "Профессионал своего дела. Гарантирую отличный результат.",
        "Высокая квалификация, индивидуальный подход к каждому клиенту.",
        "Большой опыт работы. Множество довольных клиентов.",
        "Надёжный и ответственный специалист. Работаю по всему городу.",
        "Качественная работа по разумным ценам. Обращайтесь!",
    ]

    # Create demo client
    client = User(
        name="Тест Клиент",
        phone="+998901234567",
        password_hash=pwd_context.hash("123456"),
        role="client",
        city="Toshkent",
        lang="ru",
    )
    db.add(client)
    db.flush()

    # Create demo masters
    master_profiles = []
    for i, name in enumerate(demo_names):
        phone = f"+99890{1000000 + i}"
        user = User(
            name=name,
            phone=phone,
            password_hash=pwd_context.hash("123456"),
            role="master",
            city=random.choice(cities),
            lang="ru",
        )
        db.add(user)
        db.flush()

        sub = all_subcategories[i % len(all_subcategories)]
        exp = random.randint(1, 20)
        rate = random.randint(50, 500) * 1000  # UZS

        profile = MasterProfile(
            user_id=user.id,
            subcategory_id=sub.id,
            description=random.choice(demo_descriptions_ru),
            experience_years=exp,
            hourly_rate=rate,
            city=user.city,
            skills=[sub.name_ru, f"Стаж {exp} лет"],
            rating=round(random.uniform(3.5, 5.0), 1),
            reviews_count=random.randint(0, 50),
            is_available=True,
        )
        db.add(profile)
        db.flush()
        master_profiles.append((profile, user))

    # Create some reviews
    review_comments = [
        "Отличный мастер! Рекомендую!",
        "Всё сделал быстро и качественно.",
        "Хороший специалист, буду обращаться ещё.",
        "Профессионал своего дела!",
        "Нормально, но можно было лучше.",
        "Очень доволен работой!",
    ]

    for profile, user in master_profiles[:10]:
        for _ in range(random.randint(1, 5)):
            review = Review(
                master_id=profile.id,
                client_id=client.id,
                rating=random.randint(3, 5),
                comment=random.choice(review_comments),
            )
            db.add(review)

    db.commit()
    db.close()
    print("✅ Seed data created successfully!")
    print(f"   📁 {len(categories_data)} categories")
    print(f"   📂 {len(all_subcategories)} subcategories")
    print(f"   👤 {len(demo_names)} demo masters")
    print(f"   🔑 Demo login: +998901234567 / 123456")


if __name__ == "__main__":
    seed()
