--
-- PostgreSQL database dump
--

\restrict dHUbtQ7wFphBSRTQdOV4cfWGaSPZYxcCrvO4JnHNOu4Pd2qA8g6eFqJUKaTI3fg

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

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
1	pbkdf2_sha256$870000$G2oJzv7QvgoACQ0H5ixZqN$7Z8SAPh/7V4Lm8R4GfeolmqBYNy7jkV3q62mo+kVBrI=	\N	f	manager1	علیرضا	رضایی	manager1@hotel.com	f	t	2026-11-07 14:51:22.981109+03:30	t	09121111111	manager
2	pbkdf2_sha256$870000$48n5bfn08plyJFxGJc5jGI$fRDN5ZKjZwqHsQuUX1qwtkqKXmPj1hcMrroE3FNtN1I=	\N	f	manager2	سارا	احمدی	manager2@hotel.com	f	t	2026-11-07 14:51:23.16215+03:30	t	09132222222	manager
3	pbkdf2_sha256$870000$O9gTBSwZ5fvx4JUwnLK0iJ$g13ejV8h7SflkN+naTLQjvhJdZMeI54v0bv0sS5hQxg=	\N	f	guest1	علی	محمدی	guest1@test.com	f	t	2026-11-07 14:51:23.331338+03:30	t	09123333333	guest
4	pbkdf2_sha256$870000$c43INQlwWNhtNu86Ge4Fbh$nnSYtOkrvmyTtophjYplxq4veIxtrjlHKp9lzhEVrH4=	\N	f	guest2	مریم	کریمی	guest2@test.com	f	t	2026-11-07 14:51:23.490668+03:30	t	09124444444	guest
5	pbkdf2_sha256$870000$JHRdE7NBkGEwtxAxBDuFJl$OPdBFLlR+Og0VKCF8vQm0NGhmX/CHJzMBBWyljaaj1g=	\N	f	guest3	رضا	حسینی	guest3@test.com	f	t	2026-11-07 14:51:23.650163+03:30	t	09125555555	guest
6	pbkdf2_sha256$870000$cfKUw2tvec0IilFjC0bglG$odYlqcs2qjbBo/9wULiUO3ncpfbsCKsNjfhMDuI2tFM=	\N	f	guest4	زهرا	موسوی	guest4@test.com	f	t	2026-11-07 14:51:23.809054+03:30	t	09126666666	guest
7	pbkdf2_sha256$870000$tz9lzdj5jsJiuIwAXgM2D2$Oy0fACUd7Js8S43Z/c54uNDZ28pWOUfyNiBQ5Kl+USI=	\N	f	guest5	امیر	صادقی	guest5@test.com	f	t	2026-11-07 14:51:23.967892+03:30	t	09127777777	guest
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
1	2026-10-13	2026-10-16	1	1	3	2200000	6600000	1320000	5280000	confirmed	2026-11-07 14:51:24.223035+03:30	\N	3	1	1
2	2026-10-18	2026-10-20	1	2	2	4200000	8400000	0	8400000	confirmed	2026-11-07 14:51:24.225795+03:30	\N	4	2	\N
3	2026-10-20	2026-10-24	1	2	4	3600000	14400000	2160000	12240000	confirmed	2026-11-07 14:51:24.227613+03:30	\N	5	4	3
4	2026-10-23	2026-10-26	1	2	3	5100000	15300000	3825000	11475000	confirmed	2026-11-07 14:51:24.229228+03:30	\N	6	6	4
5	2026-10-24	2026-10-28	1	2	4	4400000	17600000	1760000	15840000	confirmed	2026-11-07 14:51:24.231321+03:30	\N	7	9	5
6	2026-10-28	2026-10-31	1	2	3	3900000	11700000	2340000	9360000	confirmed	2026-11-07 14:51:24.23319+03:30	\N	3	11	6
7	2026-10-30	2026-11-02	1	2	3	4500000	13500000	2025000	11475000	confirmed	2026-11-07 14:51:24.234883+03:30	\N	4	14	7
8	2026-11-05	2026-11-09	1	2	4	4200000	16800000	3360000	13440000	confirmed	2026-11-07 14:51:24.236443+03:30	\N	5	2	1
9	2026-11-06	2026-11-10	1	2	4	5800000	23200000	0	23200000	confirmed	2026-11-07 14:51:24.238472+03:30	\N	6	5	\N
10	2026-11-04	2026-11-08	1	1	4	2800000	11200000	0	11200000	confirmed	2026-11-07 14:51:24.239798+03:30	\N	7	7	\N
11	2026-11-05	2026-11-10	1	1	5	2400000	12000000	2400000	9600000	confirmed	2026-11-07 14:51:24.241496+03:30	\N	3	12	6
12	2026-11-06	2026-11-11	1	2	5	3100000	15500000	1550000	13950000	confirmed	2026-11-07 14:51:24.242994+03:30	\N	4	16	8
13	2026-11-12	2026-11-15	1	3	3	8900000	26700000	2670000	24030000	confirmed	2026-11-07 14:51:24.245012+03:30	\N	5	3	2
14	2026-11-14	2026-11-18	1	2	4	9500000	38000000	9500000	28500000	confirmed	2026-11-07 14:51:24.246888+03:30	\N	6	8	4
15	2026-11-17	2026-11-21	1	3	4	6200000	24800000	0	24800000	confirmed	2026-11-07 14:51:24.248118+03:30	\N	7	10	\N
16	2026-11-21	2026-11-24	1	2	3	6800000	20400000	4080000	16320000	confirmed	2026-11-07 14:51:24.24964+03:30	\N	3	13	6
17	2026-11-22	2026-11-25	1	2	3	7900000	23700000	3555000	20145000	confirmed	2026-11-07 14:51:24.251412+03:30	\N	4	15	7
18	2026-11-10	2026-11-13	1	1	3	2200000	6600000	1320000	5280000	cancelled	2026-11-07 14:51:24.253266+03:30	2026-11-06 14:51:24.215846+03:30	5	1	1
19	2026-11-02	2026-11-05	1	2	3	3600000	10800000	0	10800000	cancelled	2026-11-07 14:51:24.254768+03:30	2026-11-06 14:51:24.215846+03:30	6	4	\N
20	2026-11-19	2026-11-22	1	2	3	5100000	15300000	3825000	11475000	cancelled	2026-11-07 14:51:24.256024+03:30	2026-11-06 14:51:24.215846+03:30	7	6	4
21	2026-11-27	2026-12-01	1	2	4	4300000	17200000	1720000	15480000	cancelled	2026-11-07 14:51:24.257131+03:30	2026-11-06 14:51:24.215846+03:30	3	17	8
\.


--
-- Data for Name: bookings_discountcode; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.bookings_discountcode (id, code, percent, valid_from, valid_to, max_uses, used_count, is_active, created_at, hotel_id) FROM stdin;
3	AZADI15	15	2026-10-18	2027-02-05	30	1	t	2026-11-07 14:51:24.171622+03:30	2
5	KOWSAR10	10	2026-10-08	2027-02-05	60	1	t	2026-11-07 14:51:24.189613+03:30	4
1	ESPINAS20	20	2026-10-08	2027-03-07	50	2	t	2026-11-07 14:51:24.161284+03:30	1
8	YAZD10	10	2026-09-28	2027-03-07	45	1	t	2026-11-07 14:51:24.215383+03:30	7
2	VIP10	10	2026-09-08	2027-05-06	100	1	t	2026-11-07 14:51:24.163673+03:30	1
4	ISFAHAN25	25	2026-10-23	2027-01-06	40	2	t	2026-11-07 14:51:24.18095+03:30	3
6	SHIRAZ20	20	2026-10-18	2027-02-15	50	3	t	2026-11-07 14:51:24.200038+03:30	5
7	ZAND15	15	2026-10-28	2027-01-26	25	2	t	2026-11-07 14:51:24.207878+03:30	6
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
1	contenttypes	0001_initial	2026-11-07 14:51:21.53055+03:30
2	contenttypes	0002_remove_content_type_name	2026-11-07 14:51:21.535637+03:30
3	auth	0001_initial	2026-11-07 14:51:21.56396+03:30
4	auth	0002_alter_permission_name_max_length	2026-11-07 14:51:21.567587+03:30
5	auth	0003_alter_user_email_max_length	2026-11-07 14:51:21.573538+03:30
6	auth	0004_alter_user_username_opts	2026-11-07 14:51:21.576384+03:30
7	auth	0005_alter_user_last_login_null	2026-11-07 14:51:21.579159+03:30
8	auth	0006_require_contenttypes_0002	2026-11-07 14:51:21.580093+03:30
9	auth	0007_alter_validators_add_error_messages	2026-11-07 14:51:21.583162+03:30
10	auth	0008_alter_user_username_max_length	2026-11-07 14:51:21.585766+03:30
11	auth	0009_alter_user_last_name_max_length	2026-11-07 14:51:21.58878+03:30
12	auth	0010_alter_group_name_max_length	2026-11-07 14:51:21.592456+03:30
13	auth	0011_update_proxy_permissions	2026-11-07 14:51:21.595871+03:30
14	auth	0012_alter_user_first_name_max_length	2026-11-07 14:51:21.598538+03:30
15	accounts	0001_initial	2026-11-07 14:51:21.628956+03:30
16	accounts	0002_alter_user_options_alter_user_managers_and_more	2026-11-07 14:51:21.65397+03:30
17	admin	0001_initial	2026-11-07 14:51:21.672118+03:30
18	admin	0002_logentry_remove_auto_add	2026-11-07 14:51:21.676383+03:30
19	admin	0003_logentry_add_action_flag_choices	2026-11-07 14:51:21.680706+03:30
20	hotels	0001_initial	2026-11-07 14:51:21.762143+03:30
21	bookings	0001_initial	2026-11-07 14:51:21.873288+03:30
22	reviews	0001_initial	2026-11-07 14:51:21.893911+03:30
23	sessions	0001_initial	2026-11-07 14:51:21.901691+03:30
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: hotels_amenity; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hotels_amenity (id, name, description, created_at) FROM stdin;
1	WiFi	اینترنت پرسرعت بی‌سیم رایگان در اتاق و لابی	2026-11-07 14:51:24.12998+03:30
2	Breakfast	صبحانه بوفه سلف‌سرویس گرم و سرد رایگان	2026-11-07 14:51:24.131652+03:30
3	Pool	استخر سرپوشیده، سونا، جکوزی و اسپا	2026-11-07 14:51:24.13287+03:30
4	Parking	پارکینگ اختصاصی و مسقف رایگان برای میهمانان	2026-11-07 14:51:24.134267+03:30
5	Gym	سالن بدنسازی مجهز با مربی اختصاصی	2026-11-07 14:51:24.135253+03:30
6	Room Service	خدمات اتاق و روم‌سرویس ۲۴ ساعته	2026-11-07 14:51:24.136111+03:30
7	Air Conditioning	سیستم تهویه مطبوع هوشمند فن‌کوئل	2026-11-07 14:51:24.136905+03:30
\.


--
-- Data for Name: hotels_hotel; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hotels_hotel (id, name, city, address, description, star_rating, latitude, longitude, image_url, is_active, created_at, owner_id) FROM stdin;
1	هتل اسپیناس پالاس	تهران	تهران، سعادت‌آباد، میدان بهرود، خیابان عابدی، کوچه ۳۳	هتل پنج ستاره لوکس با نمایی بی‌نظیر از شهر تهران و رشته‌کوه البرز.	5	35.789100	51.365300	https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800	t	2026-11-07 14:51:24.142018+03:30	1
2	هتل پارسیان آزادی	تهران	تهران، تقاطع بزرگراه چمران و یادگار امام	از مدرن‌ترین و با سابقه‌ترین هتل‌های پنج ستاره بین‌المللی در شمال تهران.	5	35.792500	51.388200	https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800	t	2026-11-07 14:51:24.164812+03:30	1
3	هتل عباسی	اصفهان	اصفهان، خیابان چهارباغ عباسی، خیابان آمادگاه	کهن‌ترین مهمانسرای جهان با معماری بی‌نظیر دوران صفوی و حیاط مرکزی رویایی.	5	32.651400	51.670200	https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800	t	2026-11-07 14:51:24.172698+03:30	1
4	هتل بین‌المللی کوثر	اصفهان	اصفهان، بلوار ملت، روبه‌روی سی‌وسه‌پل	هتل پنج ستاره در جوار زاینده‌رود و سی‌وسه‌پل با امکانات رفاهی ممتاز.	5	32.637100	51.666900	https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800	t	2026-11-07 14:51:24.183046+03:30	1
5	هتل بزرگ چمران	شیراز	شیراز، بلوار شهید چمران	مرتفع‌ترین هتل شیراز واقع در منطقه خوش آب‌وهوای قصرالدشت با چشم‌انداز ۳۶۰ درجه.	5	29.663100	52.488300	https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800	t	2026-11-07 14:51:24.191047+03:30	2
6	هتل سنتی زندیه	شیراز	شیراز، خیابان هجرت، پشت ارگ کریم‌خان	هتل سنتی پنج ستاره با حال‌وهوای زندیه در نزدیکی ارگ و بازار وکیل.	5	29.620000	52.530000	https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800	t	2026-11-07 14:51:24.201128+03:30	2
7	هتل داد یزد	یزد	یزد، خیابان دهم فروردین، پلاک ۲۱۴	یادگاری تاریخی از سال ۱۳۰۷ خورشیدی با معماری اصیل کویری و بادگیرهای مشهور.	4	31.884500	54.372100	https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800	t	2026-11-07 14:51:24.209254+03:30	2
\.


--
-- Data for Name: hotels_roomtype; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hotels_roomtype (id, title, description, capacity, price_per_night, quantity, created_at, hotel_id) FROM stdin;
1	اتاق یک‌تخته استاندارد	اتاق دنج و مجهز برای اقامت انفرادی کاری و توریستی.	1	2200000	6	2026-11-07 14:51:24.145731+03:30	1
2	اتاق دوتخته دلوکس	اتاق بزرگ با تخت کینگ دونفره و نمای رو به شهر.	2	4200000	10	2026-11-07 14:51:24.152845+03:30	1
3	سوئیت پرزیدنتال	سوئیت مجلل با اتاق خواب مستر، سالن نشیمن و جکوزی اختصاصی.	4	8900000	3	2026-11-07 14:51:24.156361+03:30	1
4	اتاق دوتخته توئین استاندارد	دو تخت یک‌نفره با امکانات مدرن و دسترسی سریع به بزرگراه‌ها.	2	3600000	8	2026-11-07 14:51:24.166052+03:30	2
5	سوئیت جونیور	سوئیت آرامش‌بخش مناسب سفرهای خانوادگی و کاری طولانی‌مدت.	3	5800000	4	2026-11-07 14:51:24.168985+03:30	2
6	اتاق سنتی رو به باغ	اتاق اصیل ایرانی با گچ‌بری چشم‌نواز و منظره باغ تاریخی عباسی.	2	5100000	12	2026-11-07 14:51:24.173757+03:30	3
7	اتاق یک‌تخته چشم‌انداز پردیس	اقامتی دلنشین در دل تاریخ هنر و معماری اصفهان.	1	2800000	5	2026-11-07 14:51:24.17669+03:30	3
8	سوئیت صفوی	سوئیت فاخر با نقاشی‌های تذهیب، منبت‌کاری و مبلمان دست‌ساز سنتی.	4	9500000	2	2026-11-07 14:51:24.178753+03:30	3
9	اتاق دوتخته رو به زاینده‌رود	نمای تماشایی زاینده‌رود و پل تاریخی با بالکن اختصاصی.	2	4400000	8	2026-11-07 14:51:24.184534+03:30	4
10	اتاق خانوادگی چهارنفره	دو تخت دونفره و فضای جادار برای سفرهای خانوادگی.	4	6200000	4	2026-11-07 14:51:24.186791+03:30	4
11	اتاق دوتخته دلوکس قصرالدشت	نمایی خیره‌کننده از باغات سرسبز قصرالدشت در طبقات فوقانی هتل.	2	3900000	10	2026-11-07 14:51:24.192254+03:30	5
12	اتاق یک‌تخته کینگ	تخت سایز کینگ مناسب اقامت‌های راحت و آسوده.	1	2400000	6	2026-11-07 14:51:24.194494+03:30	5
13	سوئیت رویال	مبلمان ایتالیایی، میز کار مجهز و سرویس چای و قهوه رایگان.	3	6800000	3	2026-11-07 14:51:24.197631+03:30	5
14	اتاق دو تخته سنتی دبل	دکوراسیون با کاشی‌های لاجوردی و تخت دست‌ساز چوبی.	2	4500000	8	2026-11-07 14:51:24.202748+03:30	6
15	سوئit زندیه VIP	حمام سنتی ایرانی، حیاط اختصاصی کوچک و دسترسی سریع به بافت تاریخی.	3	7900000	2	2026-11-07 14:51:24.205566+03:30	6
16	اتاق دو تخته رو به حیاط مرکزی	حوض فیروزه‌ای و کاهگل خنک در مرکز شهر بادگیرها.	2	3100000	10	2026-11-07 14:51:24.21101+03:30	7
17	اتاق سه‌تخته خانوادگی داد	فضای دلباز سنتی برای سفر خاطره‌انگیز کویری خانواده‌ها.	3	4300000	5	2026-11-07 14:51:24.213261+03:30	7
\.


--
-- Data for Name: hotels_roomtype_amenities; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hotels_roomtype_amenities (id, roomtype_id, amenity_id) FROM stdin;
1	1	1
2	1	2
3	1	7
4	2	1
5	2	2
6	2	3
7	2	6
8	2	7
9	3	1
10	3	2
11	3	3
12	3	4
13	3	5
14	3	6
15	3	7
16	4	1
17	4	2
18	4	4
19	4	7
20	5	1
21	5	2
22	5	3
23	5	5
24	5	6
25	5	7
26	6	1
27	6	2
28	6	6
29	6	7
30	7	1
31	7	2
32	7	7
33	8	1
34	8	2
35	8	4
36	8	6
37	8	7
38	9	1
39	9	2
40	9	3
41	9	5
42	9	7
43	10	1
44	10	2
45	10	4
46	10	7
47	11	1
48	11	2
49	11	3
50	11	5
51	11	6
52	11	7
53	12	1
54	12	2
55	12	4
56	12	7
57	13	1
58	13	2
59	13	3
60	13	4
61	13	5
62	13	6
63	13	7
64	14	1
65	14	2
66	14	6
67	14	7
68	15	1
69	15	2
70	15	3
71	15	4
72	15	6
73	15	7
74	16	1
75	16	2
76	16	7
77	17	1
78	17	2
79	17	4
80	17	6
81	17	7
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

SELECT pg_catalog.setval('public.accounts_user_id_seq', 7, true);


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

SELECT pg_catalog.setval('public.bookings_booking_id_seq', 21, true);


--
-- Name: bookings_discountcode_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bookings_discountcode_id_seq', 8, true);


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

SELECT pg_catalog.setval('public.hotels_amenity_id_seq', 7, true);


--
-- Name: hotels_hotel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.hotels_hotel_id_seq', 7, true);


--
-- Name: hotels_roomtype_amenities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.hotels_roomtype_amenities_id_seq', 81, true);


--
-- Name: hotels_roomtype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.hotels_roomtype_id_seq', 17, true);


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

\unrestrict dHUbtQ7wFphBSRTQdOV4cfWGaSPZYxcCrvO4JnHNOu4Pd2qA8g6eFqJUKaTI3fg

