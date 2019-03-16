from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from company_database import Company, Base, Processor, User
engine = create_engine('sqlite:///companydata.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()

User1 = User(
    name="Rajvamshi Kumar",
    email="rajvamshi.kumar@gmail.com",
    picture="https://lh3.googleusercontent.com"
    "/a-/AAuE7mCOod_gOPVv_SOu6Ev7isnVT22txvjS8_KBx1KLPw=s96")
session.add(User1)
session.commit()

company1 = Company(name="INTEL", user_id=1)
session.add(company1)
session.commit()

processor1 = Processor(
    processor_name="Intel core i9",
    about="The flagship and faster processor is the 18-core Core i9-9980XE"
          ", which is priced at $1,999. There are several other "
          "models between those, each with different number "
          "of cores or clock speed.",
    Speciality="Heavywork",
    cores="8",
    threads="16",
    cache="16Mb",
    processor_id=1,
    user_id=1
    )
session.add(processor1)
session.commit()

processor2 = Processor(
    processor_name="Intel core i7",
    about="Deliver fantastic entertainment and gaming, seamless 4K "
          "Ultra HD, and 360 video",
    Speciality="Editing",
    cores="8",
    threads="8",
    cache="12Mb",
    processor_id=1,
    user_id=1
    )
session.add(processor2)
session.commit()

processor3 = Processor(
    processor_name="Intel core i5",
    about="Intel Core i5-9600K desktop processor with Intel Turbo Boost "
          "2.0 offers powerful performance for gaming, creating and"
          " productivity of components, devices and systems",
    Speciality="Gaming",
    cores="6",
    threads="6",
    cache="9Mb",
    processor_id=1,
    user_id=1
    )
session.add(processor3)
session.commit()


company2 = Company(name="AMD", user_id=1)
session.add(company2)
session.commit()

processor1 = Processor(
    processor_name="AMD Ryzen7",
    about="Experience elite performance in games, content creation"
          ", and intensive multi-tasking. A beautifully"
          "balanced design for serious PC enthusiasts",
    Speciality="Heavywork",
    cores="8",
    threads="16",
    cache="20Mb",
    processor_id=2,
    user_id=1
    )
session.add(processor1)
session.commit()

processor2 = Processor(
    processor_name="AMD Ryzen5",
    about="Everyone deserves a powerful processor. Uncompromising "
          "features and smooth performance are finally the"
          "standard for every gamer and artist. Now including "
          "models with advanced Radeon Vega graphics built-in",
    Speciality="Editing",
    cores="6",
    threads="12",
    cache="19Mb",
    processor_id=2,
    user_id=1
    )
session.add(processor2)
session.commit()

processor3 = Processor(
    processor_name="AMD Ryzen3",
    about="Cutting-edge, true quad-core architecture provides the"
          "responsiveness and performance you'd expect from "
          "a much pricier PC. Now including models with"
          " advanced Radeon Vega graphics built-in",
    Speciality="Gaming",
    cores="4",
    threads="4",
    cache="10Mb",
    processor_id=2,
    user_id=1
    )
session.add(processor3)
session.commit()

print("List of branches are added")

