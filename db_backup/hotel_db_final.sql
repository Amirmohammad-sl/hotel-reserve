--
-- PostgreSQL database dump
--

\restrict XtJBwwPOy9dDDavwOGWMcRQ14eIujChNWcHQPKeb2nunSltiRhfITeyHjPy2And

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.reviews_review DROP CONSTRAINT IF EXISTS reviews_review_user_id_875caff2_fk_accounts_user_id;
ALTER TABLE IF EXISTS ONLY public.reviews_review DROP CONSTRAINT IF EXISTS reviews_review_hotel_id_f675fe71_fk_hotels_hotel_id;
ALTER TABLE IF EXISTS ONLY public.hotels_roomtype DROP CONSTRAINT IF EXISTS hotels_roomtype_hotel_id_04482498_fk_hotels_hotel_id;
ALTER TABLE IF EXISTS ONLY public.hotels_roomtype_amenities DROP CONSTRAINT IF EXISTS hotels_roomtype_amen_roomtype_id_8defa74b_fk_hotels_ro;
ALTER TABLE IF EXISTS ONLY public.hotels_roomtype_amenities DROP CONSTRAINT IF EXISTS hotels_roomtype_amen_amenity_id_0a6d5706_fk_hotels_am;
ALTER TABLE IF EXISTS ONLY public.hotels_hotel DROP CONSTRAINT IF EXISTS hotels_hotel_owner_id_dae0ba86_fk_accounts_user_id;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_accounts_user_id;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_content_type_id_c4bce8eb_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.bookings_discountcode DROP CONSTRAINT IF EXISTS bookings_discountcode_hotel_id_9bce04fc_fk_hotels_hotel_id;
ALTER TABLE IF EXISTS ONLY public.bookings_booking DROP CONSTRAINT IF EXISTS bookings_booking_room_type_id_6370cf99_fk_hotels_roomtype_id;
ALTER TABLE IF EXISTS ONLY public.bookings_booking DROP CONSTRAINT IF EXISTS bookings_booking_guest_id_8ba294cc_fk_accounts_user_id;
ALTER TABLE IF EXISTS ONLY public.bookings_booking DROP CONSTRAINT IF EXISTS bookings_booking_discount_code_id_019c3dc7_fk_bookings_;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_2f476e4b_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
ALTER TABLE IF EXISTS ONLY public.accounts_user_user_permissions DROP CONSTRAINT IF EXISTS accounts_user_user_p_user_id_e4f0a161_fk_accounts_;
ALTER TABLE IF EXISTS ONLY public.accounts_user_user_permissions DROP CONSTRAINT IF EXISTS accounts_user_user_p_permission_id_113bb443_fk_auth_perm;
ALTER TABLE IF EXISTS ONLY public.accounts_user_groups DROP CONSTRAINT IF EXISTS accounts_user_groups_user_id_52b62117_fk_accounts_user_id;
ALTER TABLE IF EXISTS ONLY public.accounts_user_groups DROP CONSTRAINT IF EXISTS accounts_user_groups_group_id_bd11a704_fk_auth_group_id;
DROP INDEX IF EXISTS public.reviews_review_user_id_875caff2;
DROP INDEX IF EXISTS public.reviews_review_hotel_id_f675fe71;
DROP INDEX IF EXISTS public.hotels_roomtype_hotel_id_04482498;
DROP INDEX IF EXISTS public.hotels_roomtype_amenities_roomtype_id_8defa74b;
DROP INDEX IF EXISTS public.hotels_roomtype_amenities_amenity_id_0a6d5706;
DROP INDEX IF EXISTS public.hotels_hotel_owner_id_dae0ba86;
DROP INDEX IF EXISTS public.hotels_hotel_city_1e892dbd_like;
DROP INDEX IF EXISTS public.hotels_hotel_city_1e892dbd;
DROP INDEX IF EXISTS public.hotels_amenity_name_adf4f6a4_like;
DROP INDEX IF EXISTS public.hotel_is_active_idx;
DROP INDEX IF EXISTS public.hotel_city_idx;
DROP INDEX IF EXISTS public.django_session_session_key_c0390e0f_like;
DROP INDEX IF EXISTS public.django_session_expire_date_a5c62663;
DROP INDEX IF EXISTS public.django_admin_log_user_id_c564eba6;
DROP INDEX IF EXISTS public.django_admin_log_content_type_id_c4bce8eb;
DROP INDEX IF EXISTS public.bookings_discountcode_hotel_id_9bce04fc;
DROP INDEX IF EXISTS public.bookings_booking_room_type_id_6370cf99;
DROP INDEX IF EXISTS public.bookings_booking_guest_id_8ba294cc;
DROP INDEX IF EXISTS public.bookings_booking_discount_code_id_019c3dc7;
DROP INDEX IF EXISTS public.booking_status_idx;
DROP INDEX IF EXISTS public.booking_rt_dates_idx;
DROP INDEX IF EXISTS public.booking_guest_status_idx;
DROP INDEX IF EXISTS public.auth_permission_content_type_id_2f476e4b;
DROP INDEX IF EXISTS public.auth_group_permissions_permission_id_84c5c92e;
DROP INDEX IF EXISTS public.auth_group_permissions_group_id_b120cbf9;
DROP INDEX IF EXISTS public.auth_group_name_a6ea08ec_like;
DROP INDEX IF EXISTS public.accounts_user_username_6088629e_like;
DROP INDEX IF EXISTS public.accounts_user_user_permissions_user_id_e4f0a161;
DROP INDEX IF EXISTS public.accounts_user_user_permissions_permission_id_113bb443;
DROP INDEX IF EXISTS public.accounts_user_groups_user_id_52b62117;
DROP INDEX IF EXISTS public.accounts_user_groups_group_id_bd11a704;
DROP INDEX IF EXISTS public.accounts_user_email_b2644a56_like;
ALTER TABLE IF EXISTS ONLY public.reviews_review DROP CONSTRAINT IF EXISTS unique_hotel_user_review;
ALTER TABLE IF EXISTS ONLY public.hotels_roomtype DROP CONSTRAINT IF EXISTS unique_hotel_roomtype_title;
ALTER TABLE IF EXISTS ONLY public.bookings_discountcode DROP CONSTRAINT IF EXISTS unique_hotel_discount_code;
ALTER TABLE IF EXISTS ONLY public.reviews_review DROP CONSTRAINT IF EXISTS reviews_review_pkey;
ALTER TABLE IF EXISTS ONLY public.hotels_roomtype DROP CONSTRAINT IF EXISTS hotels_roomtype_pkey;
ALTER TABLE IF EXISTS ONLY public.hotels_roomtype_amenities DROP CONSTRAINT IF EXISTS hotels_roomtype_amenities_roomtype_id_amenity_id_b1627f6a_uniq;
ALTER TABLE IF EXISTS ONLY public.hotels_roomtype_amenities DROP CONSTRAINT IF EXISTS hotels_roomtype_amenities_pkey;
ALTER TABLE IF EXISTS ONLY public.hotels_hotel DROP CONSTRAINT IF EXISTS hotels_hotel_pkey;
ALTER TABLE IF EXISTS ONLY public.hotels_amenity DROP CONSTRAINT IF EXISTS hotels_amenity_pkey;
ALTER TABLE IF EXISTS ONLY public.hotels_amenity DROP CONSTRAINT IF EXISTS hotels_amenity_name_key;
ALTER TABLE IF EXISTS ONLY public.django_session DROP CONSTRAINT IF EXISTS django_session_pkey;
ALTER TABLE IF EXISTS ONLY public.django_migrations DROP CONSTRAINT IF EXISTS django_migrations_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_app_label_model_76bd3d3b_uniq;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_pkey;
ALTER TABLE IF EXISTS ONLY public.bookings_discountcode DROP CONSTRAINT IF EXISTS bookings_discountcode_pkey;
ALTER TABLE IF EXISTS ONLY public.bookings_booking DROP CONSTRAINT IF EXISTS bookings_booking_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_codename_01ab375a_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_name_key;
ALTER TABLE IF EXISTS ONLY public.accounts_user DROP CONSTRAINT IF EXISTS accounts_user_username_key;
ALTER TABLE IF EXISTS ONLY public.accounts_user_user_permissions DROP CONSTRAINT IF EXISTS accounts_user_user_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.accounts_user_user_permissions DROP CONSTRAINT IF EXISTS accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq;
ALTER TABLE IF EXISTS ONLY public.accounts_user DROP CONSTRAINT IF EXISTS accounts_user_pkey;
ALTER TABLE IF EXISTS ONLY public.accounts_user_groups DROP CONSTRAINT IF EXISTS accounts_user_groups_user_id_group_id_59c0b32f_uniq;
ALTER TABLE IF EXISTS ONLY public.accounts_user_groups DROP CONSTRAINT IF EXISTS accounts_user_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.accounts_user DROP CONSTRAINT IF EXISTS accounts_user_email_b2644a56_uniq;
DROP TABLE IF EXISTS public.reviews_review;
DROP TABLE IF EXISTS public.hotels_roomtype_amenities;
DROP TABLE IF EXISTS public.hotels_roomtype;
DROP TABLE IF EXISTS public.hotels_hotel;
DROP TABLE IF EXISTS public.hotels_amenity;
DROP TABLE IF EXISTS public.django_session;
DROP TABLE IF EXISTS public.django_migrations;
DROP TABLE IF EXISTS public.django_content_type;
DROP TABLE IF EXISTS public.django_admin_log;
DROP TABLE IF EXISTS public.bookings_discountcode;
DROP TABLE IF EXISTS public.bookings_booking;
DROP TABLE IF EXISTS public.auth_permission;
DROP TABLE IF EXISTS public.auth_group_permissions;
DROP TABLE IF EXISTS public.auth_group;
DROP TABLE IF EXISTS public.accounts_user_user_permissions;
DROP TABLE IF EXISTS public.accounts_user_groups;
DROP TABLE IF EXISTS public.accounts_user;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounts_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.accounts_user (
    id bigint NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    email_verified boolean NOT NULL,
    phone character varying(20) NOT NULL,
    role character varying(20) NOT NULL
);


--
-- Name: accounts_user_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.accounts_user_groups (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: accounts_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.accounts_user_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.accounts_user ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_user_user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.accounts_user_user_permissions (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: accounts_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.accounts_user_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: bookings_booking; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bookings_booking (
    id bigint NOT NULL,
    check_in date NOT NULL,
    check_out date NOT NULL,
    rooms_count smallint NOT NULL,
    guests_count smallint NOT NULL,
    nights smallint NOT NULL,
    price_per_night_snapshot bigint NOT NULL,
    subtotal bigint NOT NULL,
    discount_amount bigint NOT NULL,
    total_price bigint NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    cancelled_at timestamp with time zone,
    guest_id bigint NOT NULL,
    room_type_id bigint NOT NULL,
    discount_code_id bigint,
    CONSTRAINT booking_check_out_gt_check_in CHECK ((check_out > check_in)),
    CONSTRAINT booking_guests_count_gte_1 CHECK ((guests_count >= 1)),
    CONSTRAINT booking_nights_gte_1 CHECK ((nights >= 1)),
    CONSTRAINT booking_rooms_count_gte_1 CHECK ((rooms_count >= 1)),
    CONSTRAINT bookings_booking_discount_amount_check CHECK ((discount_amount >= 0)),
    CONSTRAINT bookings_booking_guests_count_check CHECK ((guests_count >= 0)),
    CONSTRAINT bookings_booking_nights_check CHECK ((nights >= 0)),
    CONSTRAINT bookings_booking_price_per_night_snapshot_check CHECK ((price_per_night_snapshot >= 0)),
    CONSTRAINT bookings_booking_rooms_count_check CHECK ((rooms_count >= 0)),
    CONSTRAINT bookings_booking_subtotal_check CHECK ((subtotal >= 0)),
    CONSTRAINT bookings_booking_total_price_check CHECK ((total_price >= 0))
);


--
-- Name: bookings_booking_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.bookings_booking ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.bookings_booking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: bookings_discountcode; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bookings_discountcode (
    id bigint NOT NULL,
    code character varying(50) NOT NULL,
    percent smallint NOT NULL,
    valid_from date NOT NULL,
    valid_to date NOT NULL,
    max_uses integer,
    used_count integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    hotel_id bigint NOT NULL,
    CONSTRAINT bookings_discountcode_max_uses_check CHECK ((max_uses >= 0)),
    CONSTRAINT bookings_discountcode_percent_check CHECK ((percent >= 0)),
    CONSTRAINT bookings_discountcode_used_count_check CHECK ((used_count >= 0)),
    CONSTRAINT discount_percent_1_to_100 CHECK (((percent >= 1) AND (percent <= 100))),
    CONSTRAINT discount_used_count_gte_0 CHECK ((used_count >= 0)),
    CONSTRAINT discount_valid_to_gte_valid_from CHECK ((valid_to >= valid_from))
);


--
-- Name: bookings_discountcode_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.bookings_discountcode ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.bookings_discountcode_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id bigint NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


--
-- Name: hotels_amenity; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hotels_amenity (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    description text NOT NULL,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: hotels_amenity_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.hotels_amenity ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.hotels_amenity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: hotels_hotel; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hotels_hotel (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    city character varying(100) NOT NULL,
    address text NOT NULL,
    description text NOT NULL,
    star_rating smallint,
    latitude numeric(9,6),
    longitude numeric(9,6),
    image_url character varying(500) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    owner_id bigint NOT NULL,
    CONSTRAINT hotel_star_rating_1_to_5 CHECK ((((star_rating >= 1) AND (star_rating <= 5)) OR (star_rating IS NULL))),
    CONSTRAINT hotels_hotel_star_rating_check CHECK ((star_rating >= 0))
);


--
-- Name: hotels_hotel_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.hotels_hotel ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.hotels_hotel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: hotels_roomtype; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hotels_roomtype (
    id bigint NOT NULL,
    title character varying(150) NOT NULL,
    description text NOT NULL,
    capacity smallint NOT NULL,
    price_per_night bigint NOT NULL,
    quantity integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    hotel_id bigint NOT NULL,
    CONSTRAINT hotels_roomtype_capacity_check CHECK ((capacity >= 0)),
    CONSTRAINT hotels_roomtype_price_per_night_check CHECK ((price_per_night >= 0)),
    CONSTRAINT hotels_roomtype_quantity_check CHECK ((quantity >= 0)),
    CONSTRAINT roomtype_capacity_gte_1 CHECK ((capacity >= 1)),
    CONSTRAINT roomtype_quantity_gte_1 CHECK ((quantity >= 1))
);


--
-- Name: hotels_roomtype_amenities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hotels_roomtype_amenities (
    id bigint NOT NULL,
    roomtype_id bigint NOT NULL,
    amenity_id bigint NOT NULL
);


--
-- Name: hotels_roomtype_amenities_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.hotels_roomtype_amenities ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.hotels_roomtype_amenities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: hotels_roomtype_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.hotels_roomtype ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.hotels_roomtype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: reviews_review; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reviews_review (
    id bigint NOT NULL,
    rating smallint NOT NULL,
    comment text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    hotel_id bigint NOT NULL,
    user_id bigint NOT NULL,
    CONSTRAINT review_rating_1_to_5 CHECK (((rating >= 1) AND (rating <= 5))),
    CONSTRAINT reviews_review_rating_check CHECK ((rating >= 0))
);


--
-- Name: reviews_review_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.reviews_review ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.reviews_review_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: accounts_user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, email_verified, phone, role) FROM stdin;
15	pbkdf2_sha256$870000$vYSIGfLpL2W37PKOHHAsWO$k+RTfJAkCNyUdulCmFOgDbUZtl90XqDGx8RzZhM/A4g=	2026-11-08 01:06:21.999094+03:30	f	guest1	علی	محمدی	guest1@test.com	f	t	2026-11-07 00:19:35.974227+03:30	t	09123333333	guest
4	pbkdf2_sha256$870000$jFe7Ox4RWPsdS0QUGAsmsi$EOxonm29nX1629F2dmFeImVUCWPDfwRA1+vT5gzBL+U=	2026-11-08 19:49:40.480093+03:30	t	admin			admin@hotel.local	t	t	2026-11-03 02:07:57.083561+03:30	t		manager
14	pbkdf2_sha256$870000$EoWqFX6UdcAIx0e7Q8GTgl$1NcMFHa2pDXiXxByQH6NnQ1WauHyhgVLR9Ey4Qfdc3s=	\N	f	manager2	سارا	احمدی	manager2@hotel.com	f	t	2026-11-07 00:19:35.501182+03:30	t	09132222222	manager
16	pbkdf2_sha256$870000$bIp3oZwGyiw0qZGIEHhidf$0E4Bip86uxSIjWfRKQ6JV/XjsTgAvpDkH+HO7tDzhgc=	\N	f	guest2	مریم	کریمی	guest2@test.com	f	t	2026-11-07 00:19:36.5288+03:30	t	09124444444	guest
17	pbkdf2_sha256$870000$UsqcuZSkZIFadYcpzDqTbl$VaV1eTD74oc83bl2xW4kZHRG67h68+Mb93PLRdV31II=	\N	f	guest3	رضا	حسینی	guest3@test.com	f	t	2026-11-07 00:19:37.017387+03:30	t	09125555555	guest
18	pbkdf2_sha256$870000$wO6Uea7ROIgnlBqdAAZS2j$wm7QSNve4fDY0mxpvSK0d3OEU3KQQ6DPtMAFzQy2qk8=	\N	f	guest4	زهرا	موسوی	guest4@test.com	f	t	2026-11-07 00:19:37.462467+03:30	t	09126666666	guest
19	pbkdf2_sha256$870000$LxPCmLlvMgWZ67vvqpa1n5$dHLVeP10hJpvAAf9nKR76hG+20ewSdMjxfDc2W8ZCkQ=	\N	f	guest5	امیر	صادقی	guest5@test.com	f	t	2026-11-07 00:19:37.929793+03:30	t	09127777777	guest
13	pbkdf2_sha256$870000$WERioDRNe0LXOxH9cCzGq5$p6O0x+kL1t0fBsQIkgAdn6E2IlMl2Pq9veCi1qzLHRo=	2026-11-07 15:31:32.177322+03:30	f	manager1	علیرضا	رضایی	manager1@hotel.com	f	t	2026-11-07 00:19:34.93176+03:30	t	09121111111	manager
\.


--
-- Data for Name: accounts_user_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: accounts_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add user	6	add_user
22	Can change user	6	change_user
23	Can delete user	6	delete_user
24	Can view user	6	view_user
25	Can add amenity	7	add_amenity
26	Can change amenity	7	change_amenity
27	Can delete amenity	7	delete_amenity
28	Can view amenity	7	view_amenity
29	Can add hotel	8	add_hotel
30	Can change hotel	8	change_hotel
31	Can delete hotel	8	delete_hotel
32	Can view hotel	8	view_hotel
33	Can add room type	9	add_roomtype
34	Can change room type	9	change_roomtype
35	Can delete room type	9	delete_roomtype
36	Can view room type	9	view_roomtype
37	Can add discount code	10	add_discountcode
38	Can change discount code	10	change_discountcode
39	Can delete discount code	10	delete_discountcode
40	Can view discount code	10	view_discountcode
41	Can add booking	11	add_booking
42	Can change booking	11	change_booking
43	Can delete booking	11	delete_booking
44	Can view booking	11	view_booking
45	Can add review	12	add_review
46	Can change review	12	change_review
47	Can delete review	12	delete_review
48	Can view review	12	view_review
\.


--
-- Data for Name: bookings_booking; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.bookings_booking (id, check_in, check_out, rooms_count, guests_count, nights, price_per_night_snapshot, subtotal, discount_amount, total_price, status, created_at, cancelled_at, guest_id, room_type_id, discount_code_id) FROM stdin;
22	2026-10-13	2026-10-16	1	1	3	2200000	6600000	1320000	5280000	confirmed	2026-11-07 00:19:38.5456+03:30	\N	15	20	10
23	2026-10-18	2026-10-20	1	2	2	4200000	8400000	0	8400000	confirmed	2026-11-07 00:19:38.548425+03:30	\N	16	21	\N
24	2026-10-20	2026-10-24	1	2	4	3600000	14400000	2160000	12240000	confirmed	2026-11-07 00:19:38.551401+03:30	\N	17	23	12
25	2026-10-23	2026-10-26	1	2	3	5100000	15300000	3825000	11475000	confirmed	2026-11-07 00:19:38.554309+03:30	\N	18	25	13
26	2026-10-24	2026-10-28	1	2	4	4400000	17600000	1760000	15840000	confirmed	2026-11-07 00:19:38.557124+03:30	\N	19	28	14
27	2026-10-28	2026-10-31	1	2	3	3900000	11700000	2340000	9360000	confirmed	2026-11-07 00:19:38.559833+03:30	\N	15	30	15
28	2026-10-30	2026-11-02	1	2	3	4500000	13500000	2025000	11475000	confirmed	2026-11-07 00:19:38.562705+03:30	\N	16	33	16
29	2026-11-05	2026-11-09	1	2	4	4200000	16800000	3360000	13440000	confirmed	2026-11-07 00:19:38.564934+03:30	\N	17	21	10
30	2026-11-06	2026-11-10	1	2	4	5800000	23200000	0	23200000	confirmed	2026-11-07 00:19:38.567536+03:30	\N	18	24	\N
31	2026-11-04	2026-11-08	1	1	4	2800000	11200000	0	11200000	confirmed	2026-11-07 00:19:38.569491+03:30	\N	19	26	\N
32	2026-11-05	2026-11-10	1	1	5	2400000	12000000	2400000	9600000	confirmed	2026-11-07 00:19:38.571593+03:30	\N	15	31	15
33	2026-11-06	2026-11-11	1	2	5	3100000	15500000	1550000	13950000	confirmed	2026-11-07 00:19:38.574722+03:30	\N	16	35	17
34	2026-11-12	2026-11-15	1	3	3	8900000	26700000	2670000	24030000	confirmed	2026-11-07 00:19:38.577241+03:30	\N	17	22	11
35	2026-11-14	2026-11-18	1	2	4	9500000	38000000	9500000	28500000	confirmed	2026-11-07 00:19:38.580273+03:30	\N	18	27	13
36	2026-11-17	2026-11-21	1	3	4	6200000	24800000	0	24800000	confirmed	2026-11-07 00:19:38.582354+03:30	\N	19	29	\N
37	2026-11-21	2026-11-24	1	2	3	6800000	20400000	4080000	16320000	confirmed	2026-11-07 00:19:38.585117+03:30	\N	15	32	15
38	2026-11-22	2026-11-25	1	2	3	7900000	23700000	3555000	20145000	confirmed	2026-11-07 00:19:38.587528+03:30	\N	16	34	16
39	2026-11-10	2026-11-13	1	1	3	2200000	6600000	1320000	5280000	cancelled	2026-11-07 00:19:38.589903+03:30	2026-11-06 00:19:38.54341+03:30	17	20	10
40	2026-11-02	2026-11-05	1	2	3	3600000	10800000	0	10800000	cancelled	2026-11-07 00:19:38.59169+03:30	2026-11-06 00:19:38.54341+03:30	18	23	\N
41	2026-11-19	2026-11-22	1	2	3	5100000	15300000	3825000	11475000	cancelled	2026-11-07 00:19:38.593329+03:30	2026-11-06 00:19:38.54341+03:30	19	25	13
42	2026-11-27	2026-12-01	1	2	4	4300000	17200000	1720000	15480000	cancelled	2026-11-07 00:19:38.595553+03:30	2026-11-06 00:19:38.54341+03:30	15	36	17
\.


--
-- Data for Name: bookings_discountcode; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.bookings_discountcode (id, code, percent, valid_from, valid_to, max_uses, used_count, is_active, created_at, hotel_id) FROM stdin;
12	AZADI15	15	2026-10-18	2027-02-05	30	1	t	2026-11-07 00:19:38.456654+03:30	11
14	KOWSAR10	10	2026-10-08	2027-02-05	60	1	t	2026-11-07 00:19:38.501271+03:30	13
10	ESPINAS20	20	2026-10-08	2027-03-07	50	2	t	2026-11-07 00:19:38.431156+03:30	10
17	YAZD10	10	2026-09-28	2027-03-07	45	1	t	2026-11-07 00:19:38.542823+03:30	16
11	VIP10	10	2026-09-08	2027-05-06	100	1	t	2026-11-07 00:19:38.436922+03:30	10
13	ISFAHAN25	25	2026-10-23	2027-01-06	40	2	t	2026-11-07 00:19:38.484104+03:30	12
15	SHIRAZ20	20	2026-10-18	2027-02-15	50	3	t	2026-11-07 00:19:38.518526+03:30	14
16	ZAND15	15	2026-10-28	2027-01-26	25	2	t	2026-11-07 00:19:38.529262+03:30	15
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	sessions	session
6	accounts	user
7	hotels	amenity
8	hotels	hotel
9	hotels	roomtype
10	bookings	discountcode
11	bookings	booking
12	reviews	review
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2026-11-01 21:44:23.942607+03:30
2	contenttypes	0002_remove_content_type_name	2026-11-01 21:44:23.949331+03:30
3	auth	0001_initial	2026-11-01 21:44:23.994116+03:30
4	auth	0002_alter_permission_name_max_length	2026-11-01 21:44:23.999196+03:30
5	auth	0003_alter_user_email_max_length	2026-11-01 21:44:24.003229+03:30
6	auth	0004_alter_user_username_opts	2026-11-01 21:44:24.008018+03:30
7	auth	0005_alter_user_last_login_null	2026-11-01 21:44:24.011892+03:30
8	auth	0006_require_contenttypes_0002	2026-11-01 21:44:24.01317+03:30
9	auth	0007_alter_validators_add_error_messages	2026-11-01 21:44:24.016659+03:30
10	auth	0008_alter_user_username_max_length	2026-11-01 21:44:24.021671+03:30
11	auth	0009_alter_user_last_name_max_length	2026-11-01 21:44:24.025445+03:30
12	auth	0010_alter_group_name_max_length	2026-11-01 21:44:24.030134+03:30
13	auth	0011_update_proxy_permissions	2026-11-01 21:44:24.035106+03:30
14	auth	0012_alter_user_first_name_max_length	2026-11-01 21:44:24.039081+03:30
15	accounts	0001_initial	2026-11-01 21:44:24.071969+03:30
16	admin	0001_initial	2026-11-01 21:44:24.093964+03:30
17	admin	0002_logentry_remove_auto_add	2026-11-01 21:44:24.098671+03:30
18	admin	0003_logentry_add_action_flag_choices	2026-11-01 21:44:24.104033+03:30
19	sessions	0001_initial	2026-11-01 21:44:24.113659+03:30
20	accounts	0002_alter_user_options_alter_user_managers_and_more	2026-11-03 00:18:39.418705+03:30
21	hotels	0001_initial	2026-11-03 00:48:58.430204+03:30
22	bookings	0001_initial	2026-11-03 01:54:34.841527+03:30
23	reviews	0001_initial	2026-11-03 02:16:09.115908+03:30
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
4jcomfg19ax2ca7cwox38qtp07nqhm3h	.eJxVjL0OwiAYAN-F2RBAFHB09xnI94dUDU1KOxnf3ZB00PXucm-VYVtr3roseWJ1UV4dfhkCPaUNwQ9o91nT3NZlQj0SvduubzPL67q3f4MKvY6tlABYDFl00XDyRynoSYJlI8nbaIRMtIW5OIcleTk5IjCYzh5Bgvp8AQ7cORg:1xO0fE:lJy9WT0q47NLV8WDuexQ5klZOYfEi64bkVWuOBrZBmM	2026-11-17 02:08:04.916056+03:30
msvesygqcwqhyq59cid53pffd72gsayq	.eJxVjL0OwiAYAN-F2RBAFHB09xnI94dUDU1KOxnf3ZB00PXucm-VYVtr3roseWJ1UV4dfhkCPaUNwQ9o91nT3NZlQj0SvduubzPL67q3f4MKvY6tlABYDFl00XDyRynoSYJlI8nbaIRMtIW5OIcleTk5IjCYzh5Bgvp8AQ7cORg:1xO0fT:YBGGro7R5JSVDNOnFrQFHojGtOwsuNYsrrr3XSyOR-Y	2026-11-17 02:08:19.247049+03:30
yvwqab8nhwv38ndw520jnuacg0bknen6	.eJxVjL0OwiAYAN-F2RBAFHB09xnI94dUDU1KOxnf3ZB00PXucm-VYVtr3roseWJ1UV4dfhkCPaUNwQ9o91nT3NZlQj0SvduubzPL67q3f4MKvY6tlABYDFl00XDyRynoSYJlI8nbaIRMtIW5OIcleTk5IjCYzh5Bgvp8AQ7cORg:1xO0iL:_AjL-wiXzRFyGn2mIbikdtbiIN_JhBrevhCJWQVxfFY	2026-11-17 02:11:17.681478+03:30
ppy2iee9x20f4byp591428yoqqhojkaz	.eJxVjL0OwiAYAN-F2RBAFHB09xnI94dUDU1KOxnf3ZB00PXucm-VYVtr3roseWJ1UV4dfhkCPaUNwQ9o91nT3NZlQj0SvduubzPL67q3f4MKvY6tlABYDFl00XDyRynoSYJlI8nbaIRMtIW5OIcleTk5IjCYzh5Bgvp8AQ7cORg:1xPPuf:Vpx0Psa36tEGNKXEzqwmucrIRb_JVoYYR8kbovUS17s	2026-11-20 23:17:49.798737+03:30
1c6uft7gp2lhxlwhd434bakr8ltz97la	.eJxVjL0OwiAYAN-F2RBAFHB09xnI94dUDU1KOxnf3ZB00PXucm-VYVtr3roseWJ1UV4dfhkCPaUNwQ9o91nT3NZlQj0SvduubzPL67q3f4MKvY6tlABYDFl00XDyRynoSYJlI8nbaIRMtIW5OIcleTk5IjCYzh5Bgvp8AQ7cORg:1xPPux:04ydXm__AluO2E3VQjJ08UjNn2VpKievhL7UmSzIEng	2026-11-20 23:18:07.09932+03:30
32vqjnfkli7v7b55bbqbyxpslfnj7su3	.eJxVjMsOwiAQRf-FtSHDY6B06d5vIHSgFjVgSptojP-uTbrQ7T3nnhfzYV0mv7Y0-xxZzwSyw-84BLqmspF4CeVcOdWyzHngm8J32vipxnQ77u5fYApt-r4ROovKOVBGoiYnjB0hojXa6i45kpoIQSAKTcaNYlDWKSE7AoNBQdqiLbWWa_Hpcc_zk_VCgjMA7w-pFT51:1xPf8E:yDNI4LZ-mpoGvoxxecldDfRakJgEfMsJpJ0Qx4KVffc	2026-11-21 15:32:50.39884+03:30
v0850o0xow8ous4whocf1tsygrxk4vsy	.eJxVjL0OwiAYAN-F2RBAFHB09xnI94dUDU1KOxnf3ZB00PXucm-VYVtr3roseWJ1UV4dfhkCPaUNwQ9o91nT3NZlQj0SvduubzPL67q3f4MKvY6tlABYDFl00XDyRynoSYJlI8nbaIRMtIW5OIcleTk5IjCYzh5Bgvp8AQ7cORg:1xPnDG:ZdNTSJb7--7h1pfaju_wkjGMiuOVqce0styX43IUfUU	2026-11-22 00:10:34.398677+03:30
eflhyhnph7gzvcul1244jm5t2a6ljvmf	.eJxVjL0OwiAYAN-F2RBAFHB09xnI94dUDU1KOxnf3ZB00PXucm-VYVtr3roseWJ1UV4dfhkCPaUNwQ9o91nT3NZlQj0SvduubzPL67q3f4MKvY6tlABYDFl00XDyRynoSYJlI8nbaIRMtIW5OIcleTk5IjCYzh5Bgvp8AQ7cORg:1xPnDS:rex4SPl3VvzGUdg3ayqM_9oZDO-pHOqGFEPuefVywH4	2026-11-22 00:10:46.834481+03:30
ij9w5cc1vzg4j4un05p0t0li495323e3	.eJxVjsFuwyAQRP-Faxu0u7BgOPbeW-4IYxLTWhAZR0pV9d9rSzm013kzT_MtQrxvc7j3vIYyCS-QxevfcIzpM9eDTB-xXptMrW5rGeVRkU_a5Xub8vL27P4TzLHP-5phsKycA2WIdXJo7AUmtkZbPWSXSKfEgMyok3EXHJV1CmlIYDgqyLt0iX0LS7uWuvsIyJwQT2DPhF4ZTyQBgJx-AfAAx4meey-thvy4lfVLePj5BXCUSMQ:1xPo5G:YgQJhYzc40IPVvOWm575AoWcfavFYbhYy9P909YZLhs	2026-11-22 01:06:22.000576+03:30
j23rb78wlwuxa1mw666i0aowam2a3azm	.eJxVjL0OwiAYAN-F2RBAFHB09xnI94dUDU1KOxnf3ZB00PXucm-VYVtr3roseWJ1UV4dfhkCPaUNwQ9o91nT3NZlQj0SvduubzPL67q3f4MKvY6tlABYDFl00XDyRynoSYJlI8nbaIRMtIW5OIcleTk5IjCYzh5Bgvp8AQ7cORg:1xQ5cK:xPYbrMWgv5goUlmk8aS5c18EJdY4_OjWItk2EUd0j-I	2026-11-22 19:49:40.481853+03:30
kupgpjea4iwup9tv9y18o7jl9auij93x	.eJxVjDsOwjAQRO_iGlnJ-k9JnzNYa3uNA8iW4qRC3J1ESgFTznszb-ZxW4vfOi1-TuzKANjltwwYn1QPkh5Y743HVtdlDvxQ-Ek7n1qi1-10_w4K9rKvCTNhUpRHTVpqdGCGUe0xylkNWtpsDWYJaQguhgiUpCAwAlChsJl9vhDDOBc:1xQ9PP:amCzvhBXL0UlLZfgKEv1wqAjj7p2Zr0_FxnYTPBwE2A	2026-11-22 23:52:35.220429+03:30
3ntqqkkc4w42p9496xxosqwvod1iwrku	.eJxVjM0OwiAQhN-FsyGCy8969N5nIMBupGogKe3J-O7SpAdNZi7zzcxbhLitJWydlzCTuAoN4vQbppifXHdCj1jvTeZW12VOcq_Ig3Y5NeLX7ej-HZTYy1g7m41hHxV71uYy7M-cwLE1TiMCa0VIGVXmISDQ7FwCDYiWjUXx-QL9XTeh:1xQ9a3:9BrGQOc-t0p9cGCOUaz1RYzAO694kvkVzS3g2MPkuoM	2026-11-23 00:03:35.942+03:30
0vknzso09ib3an91zpk3zcgf50eplrck	.eJxVjDsOwjAQBe_iGlle_2Io6TmD5d21cQA5UpxUiLuTSCmgfTNv3iKmdalx7XmOI4uLMEqcfkdM9MxtJ_xI7T5Jmtoyjyh3RR60y9vE-XU93L9ATb1ubwjgiwXkM6cCXqF3AYltGQZrjLaMqhiyTjkdtqpDD4FT9t6RAqVJfL4EXzfr:1xQ9ls:9rI8BdfIDEbomXjVpdDto1B1Sp2QBvASJV6d48DgjCQ	2026-11-23 00:15:48.277105+03:30
k4rtpmawycmcqn5z7leagyxtdcnq0mdp	.eJxVjsEOwiAQRP-FsyEFSlc8evcbyC7LStWUpLQn47_bJj3odd6bybxVxHUpcW15jiOri3JWnX5DwvTM0074gdO96lSnZR5J74o-aNO3yvl1Pdy_gYKtbO0UEncOwWdAbwkYzNBZAQkZrRATna34RD0kS07EoAmGssfe-4G3V58vLSA46w:1xQ9m8:5vA7nDxl3-SwHD3EVZVqygpw_3IbBQyQMB50ZRxkcUw	2026-11-23 00:16:04.942776+03:30
dmsagcu01cr1v8wd26tzhk5clv92bnmm	.eJxVjDsOwjAQBe_iGln-xjIlPWew1rtrHEC2FCcV4u4QKQW0b2beSyTY1pq2wUuaSZyFncTpd8yAD247oTu0W5fY27rMWe6KPOiQ1078vBzu30GFUb-1cT4zx6KCRe3UpMkFryB4Qp8tsVPFK01EBTA6CFExa2M0ekfWahTvDwjKOB0:1xQ9nz:9gojNhLI_h8OHR_0ml7IpiVbX-REcq4w5kGLnQrLh48	2026-11-23 00:17:59.074358+03:30
\.


--
-- Data for Name: hotels_amenity; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hotels_amenity (id, name, description, created_at) FROM stdin;
2	WiFi	اینترنت پرسرعت بی‌سیم رایگان در اتاق و لابی	2026-11-07 00:19:16.225008+03:30
3	Breakfast	صبحانه بوفه سلف‌سرویس گرم و سرد رایگان	2026-11-07 00:19:16.232771+03:30
4	Pool	استخر سرپوشیده، سونا، جکوزی و اسپا	2026-11-07 00:19:16.237031+03:30
5	Parking	پارکینگ اختصاصی و مسقف رایگان برای میهمانان	2026-11-07 00:19:16.23936+03:30
6	Gym	سالن بدنسازی مجهز با مربی اختصاصی	2026-11-07 00:19:16.241923+03:30
7	Room Service	خدمات اتاق و روم‌سرویس ۲۴ ساعته	2026-11-07 00:19:16.243527+03:30
8	Air Conditioning	سیستم تهویه مطبوع هوشمند فن‌کوئل	2026-11-07 00:19:16.245419+03:30
\.


--
-- Data for Name: hotels_hotel; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hotels_hotel (id, name, city, address, description, star_rating, latitude, longitude, image_url, is_active, created_at, owner_id) FROM stdin;
2	Smoke Hotel	Tehran	Smoke St		\N	\N	\N		t	2026-11-06 23:17:49.749927+03:30	4
10	هتل اسپیناس پالاس	تهران	تهران، سعادت‌آباد، میدان بهرود، خیابان عابدی، کوچه ۳۳	هتل پنج ستاره لوکس با نمایی بی‌نظیر از شهر تهران و رشته‌کوه البرز.	5	35.789100	51.365300	https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800	t	2026-11-07 00:19:38.401828+03:30	13
11	هتل پارسیان آزادی	تهران	تهران، تقاطع بزرگراه چمران و یادگار امام	از مدرن‌ترین و با سابقه‌ترین هتل‌های پنج ستاره بین‌المللی در شمال تهران.	5	35.792500	51.388200	https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800	t	2026-11-07 00:19:38.440077+03:30	13
12	هتل عباسی	اصفهان	اصفهان، خیابان چهارباغ عباسی، خیابان آمادگاه	کهن‌ترین مهمانسرای جهان با معماری بی‌نظیر دوران صفوی و حیاط مرکزی رویایی.	5	32.651400	51.670200	https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800	t	2026-11-07 00:19:38.46013+03:30	13
13	هتل بین‌المللی کوثر	اصفهان	اصفهان، بلوار ملت، روبه‌روی سی‌وسه‌پل	هتل پنج ستاره در جوار زاینده‌رود و سی‌وسه‌پل با امکانات رفاهی ممتاز.	5	32.637100	51.666900	https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800	t	2026-11-07 00:19:38.487801+03:30	13
14	هتل بزرگ چمران	شیراز	شیراز، بلوار شهید چمران	مرتفع‌ترین هتل شیراز واقع در منطقه خوش آب‌وهوای قصرالدشت با چشم‌انداز ۳۶۰ درجه.	5	29.663100	52.488300	https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800	t	2026-11-07 00:19:38.503265+03:30	14
15	هتل سنتی زندیه	شیراز	شیراز، خیابان هجرت، پشت ارگ کریم‌خان	هتل سنتی پنج ستاره با حال‌وهوای زندیه در نزدیکی ارگ و بازار وکیل.	5	29.620000	52.530000	https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800	t	2026-11-07 00:19:38.520895+03:30	14
16	هتل داد یزد	یزد	یزد، خیابان دهم فروردین، پلاک ۲۱۴	یادگاری تاریخی از سال ۱۳۰۷ خورشیدی با معماری اصیل کویری و بادگیرهای مشهور.	4	31.884500	54.372100	https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800	t	2026-11-07 00:19:38.530987+03:30	14
\.


--
-- Data for Name: hotels_roomtype; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hotels_roomtype (id, title, description, capacity, price_per_night, quantity, created_at, hotel_id) FROM stdin;
2	Smoke Suite		2	2000000	5	2026-11-06 23:17:49.767181+03:30	2
20	اتاق یک‌تخته استاندارد	اتاق دنج و مجهز برای اقامت انفرادی کاری و توریستی.	1	2200000	6	2026-11-07 00:19:38.406763+03:30	10
21	اتاق دوتخته دلوکس	اتاق بزرگ با تخت کینگ دونفره و نمای رو به شهر.	2	4200000	10	2026-11-07 00:19:38.416907+03:30	10
22	سوئیت پرزیدنتال	سوئیت مجلل با اتاق خواب مستر، سالن نشیمن و جکوزی اختصاصی.	4	8900000	3	2026-11-07 00:19:38.42376+03:30	10
23	اتاق دوتخته توئین استاندارد	دو تخت یک‌نفره با امکانات مدرن و دسترسی سریع به بزرگراه‌ها.	2	3600000	8	2026-11-07 00:19:38.443416+03:30	11
24	سوئیت جونیور	سوئیت آرامش‌بخش مناسب سفرهای خانوادگی و کاری طولانی‌مدت.	3	5800000	4	2026-11-07 00:19:38.449797+03:30	11
25	اتاق سنتی رو به باغ	اتاق اصیل ایرانی با گچ‌بری چشم‌نواز و منظره باغ تاریخی عباسی.	2	5100000	12	2026-11-07 00:19:38.463598+03:30	12
26	اتاق یک‌تخته چشم‌انداز پردیس	اقامتی دلنشین در دل تاریخ هنر و معماری اصفهان.	1	2800000	5	2026-11-07 00:19:38.470016+03:30	12
27	سوئیت صفوی	سوئیت فاخر با نقاشی‌های تذهیب، منبت‌کاری و مبلمان دست‌ساز سنتی.	4	9500000	2	2026-11-07 00:19:38.476478+03:30	12
28	اتاق دوتخته رو به زاینده‌رود	نمای تماشایی زاینده‌رود و پل تاریخی با بالکن اختصاصی.	2	4400000	8	2026-11-07 00:19:38.490575+03:30	13
29	اتاق خانوادگی چهارنفره	دو تخت دونفره و فضای جادار برای سفرهای خانوادگی.	4	6200000	4	2026-11-07 00:19:38.495238+03:30	13
30	اتاق دوتخته دلوکس قصرالدشت	نمایی خیره‌کننده از باغات سرسبز قصرالدشت در طبقات فوقانی هتل.	2	3900000	10	2026-11-07 00:19:38.505584+03:30	14
31	اتاق یک‌تخته کینگ	تخت سایز کینگ مناسب اقامت‌های راحت و آسوده.	1	2400000	6	2026-11-07 00:19:38.509381+03:30	14
32	سوئیت رویال	مبلمان ایتالیایی، میز کار مجهز و سرویس چای و قهوه رایگان.	3	6800000	3	2026-11-07 00:19:38.514544+03:30	14
33	اتاق دو تخته سنتی دبل	دکوراسیون با کاشی‌های لاجوردی و تخت دست‌ساز چوبی.	2	4500000	8	2026-11-07 00:19:38.522572+03:30	15
34	سوئit زندیه VIP	حمام سنتی ایرانی، حیاط اختصاصی کوچک و دسترسی سریع به بافت تاریخی.	3	7900000	2	2026-11-07 00:19:38.526207+03:30	15
35	اتاق دو تخته رو به حیاط مرکزی	حوض فیروزه‌ای و کاهگل خنک در مرکز شهر بادگیرها.	2	3100000	10	2026-11-07 00:19:38.532975+03:30	16
36	اتاق سه‌تخته خانوادگی داد	فضای دلباز سنتی برای سفر خاطره‌انگیز کویری خانواده‌ها.	3	4300000	5	2026-11-07 00:19:38.538153+03:30	16
\.


--
-- Data for Name: hotels_roomtype_amenities; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hotels_roomtype_amenities (id, roomtype_id, amenity_id) FROM stdin;
83	20	8
84	20	2
85	20	3
86	21	2
87	21	3
88	21	4
89	21	7
90	21	8
91	22	2
92	22	3
93	22	4
94	22	5
95	22	6
96	22	7
97	22	8
98	23	8
99	23	2
100	23	3
101	23	5
102	24	2
103	24	3
104	24	4
105	24	6
106	24	7
107	24	8
108	25	8
109	25	2
110	25	3
111	25	7
112	26	8
113	26	2
114	26	3
115	27	2
116	27	3
117	27	5
118	27	7
119	27	8
120	28	2
121	28	3
122	28	4
123	28	6
124	28	8
125	29	8
126	29	2
127	29	3
128	29	5
129	30	2
130	30	3
131	30	4
132	30	6
133	30	7
134	30	8
135	31	8
136	31	2
137	31	3
138	31	5
139	32	2
140	32	3
141	32	4
142	32	5
143	32	6
144	32	7
145	32	8
146	33	8
147	33	2
148	33	3
149	33	7
150	34	2
151	34	3
152	34	4
153	34	5
154	34	7
155	34	8
156	35	8
157	35	2
158	35	3
159	36	2
160	36	3
161	36	5
162	36	7
163	36	8
\.


--
-- Data for Name: reviews_review; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reviews_review (id, rating, comment, created_at, updated_at, hotel_id, user_id) FROM stdin;
\.


--
-- Name: accounts_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_user_groups_id_seq', 1, false);


--
-- Name: accounts_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_user_id_seq', 45, true);


--
-- Name: accounts_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_user_user_permissions_id_seq', 1, false);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 48, true);


--
-- Name: bookings_booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bookings_booking_id_seq', 68, true);


--
-- Name: bookings_discountcode_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bookings_discountcode_id_seq', 17, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 12, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 23, true);


--
-- Name: hotels_amenity_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.hotels_amenity_id_seq', 9, true);


--
-- Name: hotels_hotel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.hotels_hotel_id_seq', 35, true);


--
-- Name: hotels_roomtype_amenities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.hotels_roomtype_amenities_id_seq', 167, true);


--
-- Name: hotels_roomtype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.hotels_roomtype_id_seq', 53, true);


--
-- Name: reviews_review_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reviews_review_id_seq', 1, false);


--
-- Name: accounts_user accounts_user_email_b2644a56_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user
    ADD CONSTRAINT accounts_user_email_b2644a56_uniq UNIQUE (email);


--
-- Name: accounts_user_groups accounts_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_groups
    ADD CONSTRAINT accounts_user_groups_pkey PRIMARY KEY (id);


--
-- Name: accounts_user_groups accounts_user_groups_user_id_group_id_59c0b32f_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_groups
    ADD CONSTRAINT accounts_user_groups_user_id_group_id_59c0b32f_uniq UNIQUE (user_id, group_id);


--
-- Name: accounts_user accounts_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user
    ADD CONSTRAINT accounts_user_pkey PRIMARY KEY (id);


--
-- Name: accounts_user_user_permissions accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_user_permissions
    ADD CONSTRAINT accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq UNIQUE (user_id, permission_id);


--
-- Name: accounts_user_user_permissions accounts_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_user_permissions
    ADD CONSTRAINT accounts_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: accounts_user accounts_user_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user
    ADD CONSTRAINT accounts_user_username_key UNIQUE (username);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: bookings_booking bookings_booking_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings_booking
    ADD CONSTRAINT bookings_booking_pkey PRIMARY KEY (id);


--
-- Name: bookings_discountcode bookings_discountcode_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings_discountcode
    ADD CONSTRAINT bookings_discountcode_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: hotels_amenity hotels_amenity_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels_amenity
    ADD CONSTRAINT hotels_amenity_name_key UNIQUE (name);


--
-- Name: hotels_amenity hotels_amenity_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels_amenity
    ADD CONSTRAINT hotels_amenity_pkey PRIMARY KEY (id);


--
-- Name: hotels_hotel hotels_hotel_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels_hotel
    ADD CONSTRAINT hotels_hotel_pkey PRIMARY KEY (id);


--
-- Name: hotels_roomtype_amenities hotels_roomtype_amenities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels_roomtype_amenities
    ADD CONSTRAINT hotels_roomtype_amenities_pkey PRIMARY KEY (id);


--
-- Name: hotels_roomtype_amenities hotels_roomtype_amenities_roomtype_id_amenity_id_b1627f6a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels_roomtype_amenities
    ADD CONSTRAINT hotels_roomtype_amenities_roomtype_id_amenity_id_b1627f6a_uniq UNIQUE (roomtype_id, amenity_id);


--
-- Name: hotels_roomtype hotels_roomtype_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels_roomtype
    ADD CONSTRAINT hotels_roomtype_pkey PRIMARY KEY (id);


--
-- Name: reviews_review reviews_review_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews_review
    ADD CONSTRAINT reviews_review_pkey PRIMARY KEY (id);


--
-- Name: bookings_discountcode unique_hotel_discount_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings_discountcode
    ADD CONSTRAINT unique_hotel_discount_code UNIQUE (hotel_id, code);


--
-- Name: hotels_roomtype unique_hotel_roomtype_title; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels_roomtype
    ADD CONSTRAINT unique_hotel_roomtype_title UNIQUE (hotel_id, title);


--
-- Name: reviews_review unique_hotel_user_review; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews_review
    ADD CONSTRAINT unique_hotel_user_review UNIQUE (hotel_id, user_id);


--
-- Name: accounts_user_email_b2644a56_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_user_email_b2644a56_like ON public.accounts_user USING btree (email varchar_pattern_ops);


--
-- Name: accounts_user_groups_group_id_bd11a704; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_user_groups_group_id_bd11a704 ON public.accounts_user_groups USING btree (group_id);


--
-- Name: accounts_user_groups_user_id_52b62117; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_user_groups_user_id_52b62117 ON public.accounts_user_groups USING btree (user_id);


--
-- Name: accounts_user_user_permissions_permission_id_113bb443; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_user_user_permissions_permission_id_113bb443 ON public.accounts_user_user_permissions USING btree (permission_id);


--
-- Name: accounts_user_user_permissions_user_id_e4f0a161; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_user_user_permissions_user_id_e4f0a161 ON public.accounts_user_user_permissions USING btree (user_id);


--
-- Name: accounts_user_username_6088629e_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_user_username_6088629e_like ON public.accounts_user USING btree (username varchar_pattern_ops);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: booking_guest_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX booking_guest_status_idx ON public.bookings_booking USING btree (guest_id, status);


--
-- Name: booking_rt_dates_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX booking_rt_dates_idx ON public.bookings_booking USING btree (room_type_id, check_in, check_out);


--
-- Name: booking_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX booking_status_idx ON public.bookings_booking USING btree (status);


--
-- Name: bookings_booking_discount_code_id_019c3dc7; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bookings_booking_discount_code_id_019c3dc7 ON public.bookings_booking USING btree (discount_code_id);


--
-- Name: bookings_booking_guest_id_8ba294cc; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bookings_booking_guest_id_8ba294cc ON public.bookings_booking USING btree (guest_id);


--
-- Name: bookings_booking_room_type_id_6370cf99; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bookings_booking_room_type_id_6370cf99 ON public.bookings_booking USING btree (room_type_id);


--
-- Name: bookings_discountcode_hotel_id_9bce04fc; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bookings_discountcode_hotel_id_9bce04fc ON public.bookings_discountcode USING btree (hotel_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: hotel_city_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hotel_city_idx ON public.hotels_hotel USING btree (city);


--
-- Name: hotel_is_active_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hotel_is_active_idx ON public.hotels_hotel USING btree (is_active);


--
-- Name: hotels_amenity_name_adf4f6a4_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hotels_amenity_name_adf4f6a4_like ON public.hotels_amenity USING btree (name varchar_pattern_ops);


--
-- Name: hotels_hotel_city_1e892dbd; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hotels_hotel_city_1e892dbd ON public.hotels_hotel USING btree (city);


--
-- Name: hotels_hotel_city_1e892dbd_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hotels_hotel_city_1e892dbd_like ON public.hotels_hotel USING btree (city varchar_pattern_ops);


--
-- Name: hotels_hotel_owner_id_dae0ba86; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hotels_hotel_owner_id_dae0ba86 ON public.hotels_hotel USING btree (owner_id);


--
-- Name: hotels_roomtype_amenities_amenity_id_0a6d5706; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hotels_roomtype_amenities_amenity_id_0a6d5706 ON public.hotels_roomtype_amenities USING btree (amenity_id);


--
-- Name: hotels_roomtype_amenities_roomtype_id_8defa74b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hotels_roomtype_amenities_roomtype_id_8defa74b ON public.hotels_roomtype_amenities USING btree (roomtype_id);


--
-- Name: hotels_roomtype_hotel_id_04482498; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hotels_roomtype_hotel_id_04482498 ON public.hotels_roomtype USING btree (hotel_id);


--
-- Name: reviews_review_hotel_id_f675fe71; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_review_hotel_id_f675fe71 ON public.reviews_review USING btree (hotel_id);


--
-- Name: reviews_review_user_id_875caff2; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_review_user_id_875caff2 ON public.reviews_review USING btree (user_id);


--
-- Name: accounts_user_groups accounts_user_groups_group_id_bd11a704_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_groups
    ADD CONSTRAINT accounts_user_groups_group_id_bd11a704_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_user_groups accounts_user_groups_user_id_52b62117_fk_accounts_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_groups
    ADD CONSTRAINT accounts_user_groups_user_id_52b62117_fk_accounts_user_id FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_user_user_permissions accounts_user_user_p_permission_id_113bb443_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_user_permissions
    ADD CONSTRAINT accounts_user_user_p_permission_id_113bb443_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_user_user_permissions accounts_user_user_p_user_id_e4f0a161_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_user_permissions
    ADD CONSTRAINT accounts_user_user_p_user_id_e4f0a161_fk_accounts_ FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bookings_booking bookings_booking_discount_code_id_019c3dc7_fk_bookings_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings_booking
    ADD CONSTRAINT bookings_booking_discount_code_id_019c3dc7_fk_bookings_ FOREIGN KEY (discount_code_id) REFERENCES public.bookings_discountcode(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bookings_booking bookings_booking_guest_id_8ba294cc_fk_accounts_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings_booking
    ADD CONSTRAINT bookings_booking_guest_id_8ba294cc_fk_accounts_user_id FOREIGN KEY (guest_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bookings_booking bookings_booking_room_type_id_6370cf99_fk_hotels_roomtype_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings_booking
    ADD CONSTRAINT bookings_booking_room_type_id_6370cf99_fk_hotels_roomtype_id FOREIGN KEY (room_type_id) REFERENCES public.hotels_roomtype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bookings_discountcode bookings_discountcode_hotel_id_9bce04fc_fk_hotels_hotel_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings_discountcode
    ADD CONSTRAINT bookings_discountcode_hotel_id_9bce04fc_fk_hotels_hotel_id FOREIGN KEY (hotel_id) REFERENCES public.hotels_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_accounts_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_accounts_user_id FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hotels_hotel hotels_hotel_owner_id_dae0ba86_fk_accounts_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels_hotel
    ADD CONSTRAINT hotels_hotel_owner_id_dae0ba86_fk_accounts_user_id FOREIGN KEY (owner_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hotels_roomtype_amenities hotels_roomtype_amen_amenity_id_0a6d5706_fk_hotels_am; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels_roomtype_amenities
    ADD CONSTRAINT hotels_roomtype_amen_amenity_id_0a6d5706_fk_hotels_am FOREIGN KEY (amenity_id) REFERENCES public.hotels_amenity(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hotels_roomtype_amenities hotels_roomtype_amen_roomtype_id_8defa74b_fk_hotels_ro; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels_roomtype_amenities
    ADD CONSTRAINT hotels_roomtype_amen_roomtype_id_8defa74b_fk_hotels_ro FOREIGN KEY (roomtype_id) REFERENCES public.hotels_roomtype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hotels_roomtype hotels_roomtype_hotel_id_04482498_fk_hotels_hotel_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels_roomtype
    ADD CONSTRAINT hotels_roomtype_hotel_id_04482498_fk_hotels_hotel_id FOREIGN KEY (hotel_id) REFERENCES public.hotels_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reviews_review reviews_review_hotel_id_f675fe71_fk_hotels_hotel_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews_review
    ADD CONSTRAINT reviews_review_hotel_id_f675fe71_fk_hotels_hotel_id FOREIGN KEY (hotel_id) REFERENCES public.hotels_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reviews_review reviews_review_user_id_875caff2_fk_accounts_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews_review
    ADD CONSTRAINT reviews_review_user_id_875caff2_fk_accounts_user_id FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

\unrestrict XtJBwwPOy9dDDavwOGWMcRQ14eIujChNWcHQPKeb2nunSltiRhfITeyHjPy2And

