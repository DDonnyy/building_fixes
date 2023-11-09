# coding: utf-8
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Enum, Float, ForeignKey, Integer, SmallInteger, String, Table, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2.types import Geometry
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


t_administrative_division = Table(
    'administrative_division', metadata,
    Column('city_id', Integer),
    Column('city', String(50)),
    Column('city_code', String(50)),
    Column('administrative_unit_id', Integer),
    Column('administrative_unit', String(50)),
    Column('municipality_id', Integer),
    Column('municipality', String(50))
)


class AdministrativeUnitType(Base):
    __tablename__ = 'administrative_unit_types'

    id = Column(Integer, primary_key=True, server_default=text("nextval('administrative_unit_types_id_seq'::regclass)"))
    full_name = Column(String(50), nullable=False, unique=True)
    short_name = Column(String(10), nullable=False, unique=True)


t_all_buildings = Table(
    'all_buildings', metadata,
    Column('building_id', Integer),
    Column('physical_object_id', Integer),
    Column('address', String(200)),
    Column('project_type', String(100)),
    Column('building_year', SmallInteger),
    Column('repair_years', String(100)),
    Column('building_area', Float),
    Column('living_area', Float),
    Column('storeys_count', SmallInteger),
    Column('central_heating', Boolean),
    Column('central_hotwater', Boolean),
    Column('central_water', Boolean),
    Column('central_electro', Boolean),
    Column('central_gas', Boolean),
    Column('refusechute', Boolean),
    Column('ukname', String(100)),
    Column('lift_count', SmallInteger),
    Column('failure', Boolean),
    Column('is_living', Boolean),
    Column('resident_number', SmallInteger),
    Column('population_balanced', SmallInteger),
    Column('properties', JSONB(astext_type=Text())),
    Column('modeled', JSONB(astext_type=Text())),
    Column('functional_object_id', Integer),
    Column('osm_id', String(50)),
    Column('geometry', Geometry(srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry')),
    Column('center', Geometry('POINT', 4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry')),
    Column('city', String(50)),
    Column('city_id', Integer),
    Column('administrative_unit', String(50)),
    Column('administrative_unit_id', Integer),
    Column('municipality', String(50)),
    Column('municipality_id', Integer),
    Column('block_id', Integer),
    Column('functional_object_created_at', DateTime(True)),
    Column('functional_object_updated_at', DateTime(True)),
    Column('physical_object_created_at', DateTime(True)),
    Column('physical_object_updated_at', DateTime(True)),
    Column('updated_at', DateTime(True)),
    Column('created_at', DateTime(True))
)


t_all_houses = Table(
    'all_houses', metadata,
    Column('building_id', Integer),
    Column('physical_object_id', Integer),
    Column('address', String(200)),
    Column('project_type', String(100)),
    Column('building_year', SmallInteger),
    Column('repair_years', String(100)),
    Column('building_area', Float),
    Column('living_area', Float),
    Column('storeys_count', SmallInteger),
    Column('central_heating', Boolean),
    Column('central_hotwater', Boolean),
    Column('central_water', Boolean),
    Column('central_electro', Boolean),
    Column('central_gas', Boolean),
    Column('refusechute', Boolean),
    Column('ukname', String(100)),
    Column('lift_count', SmallInteger),
    Column('failure', Boolean),
    Column('is_living', Boolean),
    Column('resident_number', SmallInteger),
    Column('population_balanced', SmallInteger),
    Column('properties', JSONB(astext_type=Text())),
    Column('modeled', JSONB(astext_type=Text())),
    Column('functional_object_id', Integer),
    Column('osm_id', String(50)),
    Column('geometry', Geometry(srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry')),
    Column('center', Geometry('POINT', 4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry')),
    Column('city', String(50)),
    Column('city_id', Integer),
    Column('administrative_unit', String(50)),
    Column('administrative_unit_id', Integer),
    Column('municipality', String(50)),
    Column('municipality_id', Integer),
    Column('block_id', Integer),
    Column('functional_object_created_at', DateTime(True)),
    Column('functional_object_updated_at', DateTime(True)),
    Column('physical_object_created_at', DateTime(True)),
    Column('physical_object_updated_at', DateTime(True)),
    Column('updated_at', DateTime(True)),
    Column('created_at', DateTime(True))
)


t_all_services = Table(
    'all_services', metadata,
    Column('functional_object_id', Integer),
    Column('physical_object_id', Integer),
    Column('building_id', Integer),
    Column('geometry', Geometry(srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry')),
    Column('center', Geometry('POINT', 4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry')),
    Column('city_service_type', String(50)),
    Column('city_service_type_id', Integer),
    Column('city_service_type_code', String(50)),
    Column('city_function', String(50)),
    Column('city_function_id', Integer),
    Column('city_function_code', String(50)),
    Column('infrastructure_type', String(50)),
    Column('infrastructure_type_id', Integer),
    Column('infrastructure_type_code', String(50)),
    Column('service_name', String(200)),
    Column('opening_hours', String(200)),
    Column('website', String(200)),
    Column('phone', String(100)),
    Column('capacity', Integer),
    Column('is_capacity_real', Boolean),
    Column('address', String(200)),
    Column('is_living', Boolean),
    Column('city', String(50)),
    Column('city_id', Integer),
    Column('administrative_unit', String(50)),
    Column('administrative_unit_id', Integer),
    Column('municipality', String(50)),
    Column('municipality_id', Integer),
    Column('block_id', Integer),
    Column('building_properties', JSONB(astext_type=Text())),
    Column('functional_object_properties', JSONB(astext_type=Text())),
    Column('building_modeled', JSONB(astext_type=Text())),
    Column('functional_object_modeled', JSONB(astext_type=Text())),
    Column('functional_object_created_at', DateTime(True)),
    Column('functional_object_updated_at', DateTime(True)),
    Column('physical_object_created_at', DateTime(True)),
    Column('physical_object_updated_at', DateTime(True)),
    Column('updated_at', DateTime(True)),
    Column('created_at', DateTime(True))
)


t_cities_statistics = Table(
    'cities_statistics', metadata,
    Column('id', Integer),
    Column('name', String(50)),
    Column('unique_service_types', Integer),
    Column('total_services', Integer),
    Column('living_houses', Integer),
    Column('buildings', Integer),
    Column('updated_at', DateTime(True))
)


class CityInfrastructureType(Base):
    __tablename__ = 'city_infrastructure_types'

    id = Column(Integer, primary_key=True, server_default=text("nextval('city_infrastructure_types_id_seq'::regclass)"))
    name = Column(String(50), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True)


t_geography_columns = Table(
    'geography_columns', metadata,
    Column('f_table_catalog', String),
    Column('f_table_schema', String),
    Column('f_table_name', String),
    Column('f_geography_column', String),
    Column('coord_dimension', Integer),
    Column('srid', Integer),
    Column('type', Text)
)


t_geometry_columns = Table(
    'geometry_columns', metadata,
    Column('f_table_catalog', String(256)),
    Column('f_table_schema', String),
    Column('f_table_name', String),
    Column('f_geometry_column', String),
    Column('coord_dimension', Integer),
    Column('srid', Integer),
    Column('type', String(30))
)


t_houses = Table(
    'houses', metadata,
    Column('building_id', Integer),
    Column('physical_object_id', Integer),
    Column('address', String(200)),
    Column('project_type', String(100)),
    Column('building_year', SmallInteger),
    Column('repair_years', String(100)),
    Column('building_area', Float),
    Column('living_area', Float),
    Column('storeys_count', SmallInteger),
    Column('central_heating', Boolean),
    Column('central_hotwater', Boolean),
    Column('central_water', Boolean),
    Column('central_electro', Boolean),
    Column('central_gas', Boolean),
    Column('refusechute', Boolean),
    Column('ukname', String(100)),
    Column('lift_count', SmallInteger),
    Column('failure', Boolean),
    Column('is_living', Boolean),
    Column('resident_number', SmallInteger),
    Column('population_balanced', SmallInteger),
    Column('properties', JSONB(astext_type=Text())),
    Column('modeled', JSONB(astext_type=Text())),
    Column('functional_object_id', Integer),
    Column('osm_id', String(50)),
    Column('geometry', Geometry(srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry')),
    Column('center', Geometry('POINT', 4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry')),
    Column('city', String(50)),
    Column('city_id', Integer),
    Column('administrative_unit', String(50)),
    Column('administrative_unit_id', Integer),
    Column('municipality', String(50)),
    Column('municipality_id', Integer),
    Column('block_id', Integer),
    Column('functional_object_created_at', DateTime(True)),
    Column('functional_object_updated_at', DateTime(True)),
    Column('physical_object_created_at', DateTime(True)),
    Column('physical_object_updated_at', DateTime(True)),
    Column('updated_at', DateTime(True)),
    Column('created_at', DateTime(True))
)


class LivingSituation(Base):
    __tablename__ = 'living_situations'

    id = Column(Integer, primary_key=True, server_default=text("nextval('living_situations_id_seq'::regclass)"))
    name = Column(String, nullable=False, unique=True)


class MunicipalityType(Base):
    __tablename__ = 'municipality_types'

    id = Column(Integer, primary_key=True, server_default=text("nextval('municipality_types_id_seq'::regclass)"))
    full_name = Column(String(50), nullable=False, unique=True)
    short_name = Column(String(10), nullable=False, unique=True)


class Region(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True, server_default=text("nextval('regions_id_seq'::regclass)"))
    name = Column(String(50), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True)
    geometry = Column(Geometry(srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    center = Column(Geometry('POINT', 4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(True), nullable=False, server_default=text("now()"))


t_service_hierarchy = Table(
    'service_hierarchy', metadata,
    Column('infrastructure_id', Integer),
    Column('infrastructure', String(50)),
    Column('infrastructure_code', String(50)),
    Column('city_function_id', Integer),
    Column('city_function', String(50)),
    Column('city_function_code', String(50)),
    Column('city_service_type_id', Integer),
    Column('city_service_type', String(50)),
    Column('city_service_type_code', String(50))
)


class SocialGroup(Base):
    __tablename__ = 'social_groups'

    id = Column(Integer, primary_key=True, server_default=text("nextval('social_groups_id_seq'::regclass)"))
    name = Column(String, nullable=False, unique=True)
    code = Column(String, nullable=False, unique=True)
    parent_id = Column(ForeignKey('social_groups.id', deferrable=True, initially='DEFERRED'))
    social_group_value = Column(Float(53))

    parent = relationship('SocialGroup', remote_side=[id])


class SpatialRefSy(Base):
    __tablename__ = 'spatial_ref_sys'
    __table_args__ = (
        CheckConstraint('(srid > 0) AND (srid <= 998999)'),
    )

    srid = Column(Integer, primary_key=True)
    auth_name = Column(String(256))
    auth_srid = Column(Integer)
    srtext = Column(String(2048))
    proj4text = Column(String(2048))


t_table_sizes = Table(
    'table_sizes', metadata,
    Column('table_name', Text),
    Column('table_size', Text),
    Column('indexes_size', Text),
    Column('total_size', Text)
)


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, server_default=text("nextval('cities_id_seq'::regclass)"))
    name = Column(String(50), nullable=False, unique=True)
    geometry = Column(Geometry(srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    center = Column(Geometry('POINT', 4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    population = Column(Integer)
    created_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    city_division_type = Column(Enum('ADMIN_UNIT_PARENT', 'MUNICIPALITY_PARENT', 'NO_PARENT', name='city_division_type'), nullable=False)
    local_crs = Column(Integer)
    code = Column(String(50))
    region_id = Column(ForeignKey('regions.id'))

    region = relationship('Region')


class CityFunction(Base):
    __tablename__ = 'city_functions'

    id = Column(Integer, primary_key=True, server_default=text("nextval('city_functions_id_seq'::regclass)"))
    city_infrastructure_type_id = Column(ForeignKey('city_infrastructure_types.id'))
    name = Column(String(50), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True)

    city_infrastructure_type = relationship('CityInfrastructureType')


class AdministrativeUnit(Base):
    __tablename__ = 'administrative_units'

    id = Column(Integer, primary_key=True, server_default=text("nextval('administrative_units_id_seq'::regclass)"))
    parent_id = Column(ForeignKey('administrative_units.id'))
    city_id = Column(ForeignKey('cities.id'), nullable=False, index=True)
    type_id = Column(ForeignKey('administrative_unit_types.id'), nullable=False)
    name = Column(String(50), nullable=False)
    geometry = Column(Geometry(srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    center = Column(Geometry('POINT', 4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    population = Column(Integer)
    created_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    municipality_parent_id = Column(Integer)

    city = relationship('City')
    parent = relationship('AdministrativeUnit', remote_side=[id])
    type = relationship('AdministrativeUnitType')


class CityServiceType(Base):
    __tablename__ = 'city_service_types'

    id = Column(Integer, primary_key=True, server_default=text("nextval('city_service_types_id_seq'::regclass)"))
    city_function_id = Column(ForeignKey('city_functions.id'), nullable=False)
    name = Column(String(50), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True)
    capacity_min = Column(Integer, nullable=False)
    capacity_max = Column(Integer, nullable=False)
    status_min = Column(SmallInteger, nullable=False)
    status_max = Column(SmallInteger, nullable=False)
    is_building = Column(Boolean, nullable=False)
    public_transport_time_normative = Column(Integer)
    walking_radius_normative = Column(Integer)

    city_function = relationship('CityFunction')


class Municipality(Base):
    __tablename__ = 'municipalities'

    id = Column(Integer, primary_key=True, server_default=text("nextval('municipalities_id_seq'::regclass)"))
    parent_id = Column(ForeignKey('municipalities.id'))
    city_id = Column(ForeignKey('cities.id'), nullable=False, index=True)
    type_id = Column(ForeignKey('municipality_types.id'), nullable=False)
    name = Column(String(50), nullable=False)
    geometry = Column(Geometry(srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    center = Column(Geometry('POINT', 4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    population = Column(Integer)
    created_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    admin_unit_parent_id = Column(Integer)

    city = relationship('City')
    parent = relationship('Municipality', remote_side=[id])
    type = relationship('MunicipalityType')


class AgeSexSocialStatAdministrativeUnit(Base):
    __tablename__ = 'age_sex_social_stat_administrative_units'

    year = Column(SmallInteger, primary_key=True, nullable=False)
    administrative_unit_id = Column(ForeignKey('administrative_units.id'), primary_key=True, nullable=False)
    social_group_id = Column(ForeignKey('social_groups.id'), primary_key=True, nullable=False)
    age = Column(SmallInteger, primary_key=True, nullable=False)
    men = Column(Integer)
    women = Column(Integer)

    administrative_unit = relationship('AdministrativeUnit')
    social_group = relationship('SocialGroup')


class AgeSexStatMunicipality(Base):
    __tablename__ = 'age_sex_stat_municipalities'

    year = Column(SmallInteger, primary_key=True, nullable=False)
    municipality_id = Column(ForeignKey('municipalities.id'), primary_key=True, nullable=False)
    age = Column(SmallInteger, primary_key=True, nullable=False)
    men = Column(Integer)
    women = Column(Integer)

    municipality = relationship('Municipality')


class Block(Base):
    __tablename__ = 'blocks'

    id = Column(Integer, primary_key=True, server_default=text("nextval('blocks_id_seq'::regclass)"))
    city_id = Column(ForeignKey('cities.id'), index=True)
    geometry = Column(Geometry(srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    center = Column(Geometry('POINT', 4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    population = Column(Integer)
    created_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    municipality_id = Column(ForeignKey('municipalities.id'))
    administrative_unit_id = Column(ForeignKey('administrative_units.id'))
    area = Column(Float(53))

    administrative_unit = relationship('AdministrativeUnit')
    city = relationship('City')
    municipality = relationship('Municipality')


class PhysicalObject(Base):
    __tablename__ = 'physical_objects'

    id = Column(Integer, primary_key=True, server_default=text("nextval('physical_objects_id_seq'::regclass)"))
    osm_id = Column(String(50))
    geometry = Column(Geometry(srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    center = Column(Geometry('POINT', 4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False)
    city_id = Column(ForeignKey('cities.id'), nullable=False, index=True)
    municipality_id = Column(ForeignKey('municipalities.id'), index=True)
    administrative_unit_id = Column(ForeignKey('administrative_units.id'), index=True)
    block_id = Column(ForeignKey('blocks.id'), index=True)
    created_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(True), nullable=False, server_default=text("now()"))

    administrative_unit = relationship('AdministrativeUnit')
    block = relationship('Block')
    city = relationship('City')
    municipality = relationship('Municipality')


class Building(Base):
    __tablename__ = 'buildings'

    id = Column(Integer, primary_key=True, server_default=text("nextval('buildings_id_seq'::regclass)"))
    physical_object_id = Column(ForeignKey('physical_objects.id'), unique=True)
    address = Column(String(200))
    project_type = Column(String(100))
    building_area = Column(Float)
    living_area = Column(Float)
    storeys_count = Column(SmallInteger)
    resident_number = Column(SmallInteger)
    central_heating = Column(Boolean)
    central_hotwater = Column(Boolean)
    central_electro = Column(Boolean)
    central_gas = Column(Boolean)
    refusechute = Column(Boolean)
    ukname = Column(String(100))
    failure = Column(Boolean)
    lift_count = Column(SmallInteger)
    repair_years = Column(String(100))
    is_living = Column(Boolean)
    population_balanced = Column(SmallInteger, server_default=text("0"))
    central_water = Column(Boolean)
    modeled = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    building_year = Column(SmallInteger)
    properties = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))

    physical_object = relationship('PhysicalObject', uselist=False)


class FunctionalObject(Base):
    __tablename__ = 'functional_objects'

    id = Column(Integer, primary_key=True, server_default=text("nextval('functional_objects_id_seq'::regclass)"))
    name = Column(String(200))
    opening_hours = Column(String(200))
    website = Column(String(200))
    phone = Column(String(100))
    capacity = Column(Integer, nullable=False)
    city_infrastructure_type_id = Column(ForeignKey('city_infrastructure_types.id'), nullable=False)
    city_function_id = Column(ForeignKey('city_functions.id'), nullable=False)
    city_service_type_id = Column(ForeignKey('city_service_types.id'), nullable=False, index=True)
    created_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    physical_object_id = Column(ForeignKey('physical_objects.id'), index=True)
    is_capacity_real = Column(Boolean)
    properties = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    modeled = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))

    city_function = relationship('CityFunction')
    city_infrastructure_type = relationship('CityInfrastructureType')
    city_service_type = relationship('CityServiceType')
    physical_object = relationship('PhysicalObject')